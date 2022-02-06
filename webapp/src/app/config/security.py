from fastapi import Security , HTTPException , status
from fastapi.security.api_key import APIKeyHeader
import os

api_key_name = os.environ.get("api_key_name",'API-KEY')
api_key =  os.environ.get("api_key",'1234567890')

api_key_header_auth = APIKeyHeader(name=api_key_name, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )