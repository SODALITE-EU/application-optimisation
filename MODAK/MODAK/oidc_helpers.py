from typing import Awaitable, Callable, List, Mapping, Optional, Union

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
    @cached(ttl=cache_ttl, key=lambda d: d["jwks_uri"])
    async def get_authentication_server_public_keys(OIDC_spec: Mapping):
        """
        Retrieve the public keys used by the authentication server
        for signing OIDC ID tokens.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(OIDC_spec["jwks_uri"])
        resp.raise_for_status()
        return resp.json()
        # return [key for key in jwks["keys"] if key["kid"]]

    def get_signing_algos(OIDC_spec: Mapping):
        return OIDC_spec["id_token_signing_alg_values_supported"]

    @cached(ttl=cache_ttl)
    async def discover_auth_server(base_url: str) -> Mapping:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{base_url}/.well-known/openid-configuration")
        resp.raise_for_status()
        return resp.json()

    return (
        discover_auth_server,
        get_authentication_server_public_keys,
        get_signing_algos,
    )


def get_auth(
    client_id: str,
    base_authorization_server_uri: str,
    signature_cache_ttl: int,
    audience: Optional[str] = None,
    issuer: Optional[str] = None,
) -> Callable[[str], Awaitable[Mapping]]:
    """Take configurations and return the authenticate_user function.
    This function should only be invoked once at the beggining of your
    server code. The function it returns should be used to check user credentials.
    Args:
        client_id (str): This string is provided when you register with your resource
            server.
        base_authorization_server_uri(URL): Everything before /.wellknow in your auth
            server URL. I.E. https://dev-123456.okta.com
        issuer (URL): Same as base_authorization. This is used to generating OpenAPI3.0
            docs which is broken (in OpenAPI/FastAPI) right now.
            Defauilts to the base_authorization_server_uri.
        signature_cache_ttl (int): How many seconds your app should cache the
            authorization server's public signatures.
        audience (str): (Optional) The audience string configured by your auth server.
            If not set defaults to client_id
        token_type (IDToken or subclass): (Optional) An optional class to be returned by
            the authenticate_user function.
    Returns:
        func: authenticate_user(auth_header: str) -> IDToken (or token_type)
    Raises:
        Nothing intentional
    """

    oauth2_scheme = OpenIdConnect(
        openIdConnectUrl=f"{base_authorization_server_uri}/.well-known/openid-configuration"
    )

    auth_server, public_keys, signing_algos = configure(cache_ttl=signature_cache_ttl)

    async def authenticate_user(
        auth_header: str = Depends(oauth2_scheme),  # noqa: B008
    ) -> Mapping:
        """Validate and parse OIDC ID token against issuer in config.
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
        OIDC_discoveries = await auth_server(base_url=base_authorization_server_uri)
        key = await public_keys(OIDC_discoveries)
        algorithms = signing_algos(OIDC_discoveries)

        # Note: keycloak seems to violate the OIDC spec by not adding
        #       the client_id to the 'aud' claim (always contains all
        #       other claims the user may have access to).
        # TODO: Instead, the 'azp' claim is filled and might to be checked.
        try:
            token = jwt.decode(
                id_token,
                key,
                algorithms,
                audience=audience if audience else client_id,
                issuer=issuer if issuer else base_authorization_server_uri,
                options={"verify_aud": False},
            )
            return token

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            # TODO: log the original error here
            raise HTTPException(
                status_code=401, detail=f"Unauthorized: {err}"
            ) from None

    return authenticate_user
