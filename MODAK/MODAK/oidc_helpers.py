from typing import Awaitable, Callable, List, Mapping, Union

import httpx
from aiocache import cached
from fastapi import Depends, HTTPException
from fastapi.security import OpenIdConnect
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError
from typing_extensions import Protocol

# Much of this was inspired by https://github.com/HarryMWinters/fastapi-oidc
# with some noteable differences: everything here is async


class IDToken(Protocol):
    iss: str
    sub: str
    aud: Union[str, List[str]]
    exp: int
    iat: int


def configure(cache_ttl: int = 3600):
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


def get_auth(
    client_id: str,
    base_authorization_server_uri: str,
    signature_cache_ttl: int,
) -> Callable[[str], Awaitable[Mapping]]:
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
    """

    oauth2_scheme = OpenIdConnect(
        openIdConnectUrl=f"{base_authorization_server_uri}/.well-known/openid-configuration"
    )

    auth_server, public_keys = configure(cache_ttl=signature_cache_ttl)

    async def authenticate_user(
        auth_header: str = Depends(oauth2_scheme),  # noqa: B008
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
        id_token = auth_header.split(" ")[-1]
        discovery_spec = await auth_server(base_url=base_authorization_server_uri)
        key = await public_keys(discovery_spec["jwks_uri"])
        algorithms = discovery_spec["id_token_signing_alg_values_supported"]

        # Note: keycloak seems to violate the OIDC spec by not adding
        #       the client_id to the 'aud' claim (always contains all
        #       other claims the user may have access to).
        # TODO: Instead, the 'azp' claim is filled and might to be checked.
        try:
            token = jwt.decode(
                id_token,
                key,
                algorithms,
                issuer=discovery_spec["issuer"],
                options={"verify_aud": False},
            )
            return token

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            # TODO: log the original error here
            raise HTTPException(
                status_code=401, detail=f"Unauthorized: {err}"
            ) from None

    return authenticate_user
