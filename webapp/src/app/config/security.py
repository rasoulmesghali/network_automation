from fastapi import Security , HTTPException , status
from fastapi.security.api_key import APIKeyHeader
from functools import lru_cache
from config import env


@lru_cache()
def get_settings():
    return env.Settings()

api_key_name = get_settings().api_key_name
api_key =  get_settings().api_key

api_key_header_auth = APIKeyHeader(name=api_key_name, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )