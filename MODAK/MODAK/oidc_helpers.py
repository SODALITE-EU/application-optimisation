import re
from typing import Mapping, Optional
from uuid import uuid4

import httpx
from aiocache import cached
from fastapi import HTTPException, status
from fastapi.security import OpenIdConnect, SecurityScopes
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from loguru import logger
from starlette.requests import Request

# Much of this was inspired by https://github.com/HarryMWinters/fastapi-oidc
# with some noteable differences: everything here is async


ROLE_MATCH = r"(?P<type>\w+)_(?P<permissions>\w)"


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


class ExtendedOpenIdConnect(OpenIdConnect):
    def __init__(
        self,
        client_id: str,
        base_authorization_server_url: Optional[str],
        signature_cache_ttl: int = 3600,
        api_key: Optional[str] = None,
    ):
        if not base_authorization_server_url:
            base_authorization_server_url = ""

        self.base_authorization_server_url = base_authorization_server_url

        super().__init__(
            openIdConnectUrl=f"{base_authorization_server_url}/.well-known/openid-configuration"
        )

        self.client_id = client_id
        self.auth_server, self.public_keys = configure_oidc(
            cache_ttl=signature_cache_ttl
        )

        if api_key == "":
            api_key = uuid4().hex
            logger.info(f"Generated API Key: {api_key}")

        self.api_key = api_key

    async def __call__(  # type: ignore
        self,
        request: Request,
        security_scopes: SecurityScopes,
    ) -> Optional[Mapping]:
        """Validate and parse OIDC ID token against issuer in discovery.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.
        Args:
            auth_header (str): Base64 encoded OIDC Token. This is invoked behind the
                scenes by Depends.
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

        auth_header_oidc = await super().__call__(request)
        if not auth_header_oidc:
            raise credentials_exception

        id_token = auth_header_oidc.split(" ")[-1]

        if id_token == self.api_key:
            logger.info("Authenticated request by api key")
            return {"scope": ["apiKey"]}

        if not self.base_authorization_server_url:
            raise HTTPException(status_code=401, detail="Unauthorized")

        discovery_spec = await self.auth_server(
            base_url=self.base_authorization_server_url
        )
        key = await self.public_keys(discovery_spec["jwks_uri"])
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

        if ("modak", "r") not in token_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

        return token
