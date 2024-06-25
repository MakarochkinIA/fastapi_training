from typing import Union
import aiohttp
from starlette import status
from starlette.datastructures import Headers

from config import settings
from exceptions import HeadersValidationError, AuthenticationError
from typing import Any


def is_user_recipient(
        user_id: Union[str, int], message: dict[str, Any]
) -> bool:
    return user_id == message.get("recipient_id")


# Retrieving the authorization token from the incoming request header
def get_headers_token(headers: Headers) -> Union[str, None]:
    authorization_header = headers.get("authorization")
    if authorization_header is None:
        raise HeadersValidationError(
            msg="Credentials are not provided.",
            status=status.HTTP_403_FORBIDDEN
        )
    if authorization_header.startswith("Bearer "):
        return authorization_header
    raise HeadersValidationError(
        msg="Incorrect token type.", status=status.HTTP_403_FORBIDDEN
    )


# Check authorization token's validity
async def is_user_authenticated(token: str) -> Union[str, None]:
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(
                    f"{settings.MAIN_HOST}/api/v1/is_user_auth/",
                    headers={"Authorization": token}
            )
        except aiohttp.ClientError:
            raise AuthenticationError(
                msg="Authentication API connection error.",
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        if response.ok:
            return await response.json()
        raise AuthenticationError(
            msg=response, status=status.HTTP_401_UNAUTHORIZED
        )
