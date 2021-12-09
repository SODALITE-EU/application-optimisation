import re
from typing import Awaitable, Callable, List, Mapping, Optional, Union
from uuid import uuid4

import httpx
from aiocache import cached
from fastapi import Depends, HTTPException, status
from fastapi.security import OpenIdConnect, SecurityScopes
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from loguru import logger
from typing_extensions import Protocol

# Much of this was inspired by https://github.com/HarryMWinters/fastapi-oidc
# with some noteable differences: everything here is async


ROLE_MATCH = r"(?P<type>\w+)_(?P<permissions>\w)"


class IDToken(Protocol):
    iss: str
    sub: str
    aud: Union[str, List[str]]
    exp: int
    iat: int


def configure_oidc(cache_ttl: int = 3600):
    @cached(ttl=cache_ttl)
    async def get_authentication_server_public_keys(jwks_uri: str) -> Mapping:
        """
        Retrieve the public keys used by the authentication server
        for signing OIDC ID tokens.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(jwks_uri)
        resp.raise_for_status()
        return resp.json()

    @cached(ttl=cache_ttl)
    async def discover_auth_server(base_url: str) -> Mapping:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/.well-known/openid-configuration")
        resp.raise_for_status()
        return resp.json()

    return (
        discover_auth_server,
        get_authentication_server_public_keys,
    )


def get_auth_token(
    client_id: str,
    base_authorization_server_url: Optional[str],
    signature_cache_ttl: int = 3600,
    api_key: Optional[str] = None,
) -> Callable[[SecurityScopes, str], Awaitable[Mapping]]:
    """Take configurations and return the authenticate_user function.
    This function should only be invoked once at the beggining of your
    server code. The function it returns should be used to check user credentials.
    Args:
        client_id (str): This string is provided when you register with your resource
            server.
        base_authorization_server_uri(URL): Everything before /.wellknow in your auth
            server URL. I.E. https://dev-123456.okta.com
        signature_cache_ttl (int): How many seconds your app should cache the
            authorization server's public signatures.
        api_key (str): Optional universal API key.
    """

    if not base_authorization_server_url:
        base_authorization_server_url = ""

    oidc_scheme = OpenIdConnect(
        openIdConnectUrl=f"{base_authorization_server_url}/.well-known/openid-configuration"
    )

    auth_server, public_keys = configure_oidc(cache_ttl=signature_cache_ttl)
    auth_server, public_keys = configure_oidc(cache_ttl=signature_cache_ttl)
    if api_key == "":
        api_key = uuid4().hex
        logger.info(f"Generated API Key: {api_key}")

    async def authenticated_token(
        security_scopes: SecurityScopes,
        auth_header_oidc: str = Depends(oidc_scheme),  # noqa: B008
    ) -> Mapping:
        """Validate and parse OIDC ID token against issuer in discovery.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.
        Args:
            auth_header (str): Base64 encoded OIDC Token. This is invoked behind the
                scenes by Depends.
        Return:
            IDToken (types.IDToken):
        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
        """

        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )

        id_token = auth_header_oidc.split(" ")[-1]

        if id_token == api_key:
            logger.info("Authenticated request by api key")
            return {"scope": ["apiKey"]}

        if not base_authorization_server_url:
            raise HTTPException(status_code=401, detail="Unauthorized")

        discovery_spec = await auth_server(base_url=base_authorization_server_url)
        key = await public_keys(discovery_spec["jwks_uri"])
        algorithms = discovery_spec["id_token_signing_alg_values_supported"]

        # Note: keycloak seems to violate the OIDC spec by not adding
        #       the client_id to the 'aud' claim (always contains all
        #       other claims the user may have access to).

        try:
            token = jwt.decode(
                id_token,
                key,
                algorithms,
                issuer=discovery_spec["issuer"],
                options={"verify_aud": False},
            )
        except ExpiredSignatureError:
            logger.info("Unsuccessful login attempt with expired signature")
            raise credentials_exception from None
        except (JWTError, JWTClaimsError) as err:
            logger.warning(f"Invalid JWT data or claim validation failed: {err}")
            raise credentials_exception from None

        for scope in security_scopes.scopes:
            if scope not in token.get("scopes", []):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

        token_roles = []

        try:
            for role in token["resource_access"][token["azp"]]["roles"]:
                match = re.match(ROLE_MATCH, role)

                if match:
                    token_roles.append(match.groups())
        except KeyError:
            logger.warning("Presented token did not contain required attributes")
            raise credentials_exception from None

        print(token_roles)
        if ("modak", "r") not in token_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

        return token

    return authenticated_token
