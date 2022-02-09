from pydantic import BaseSettings


class Settings(BaseSettings):
    
    monogodb_url: str = "mongodb://root:root@127.0.0.1:27017"
    monogodb_db: str = "db1"
    monogodb_collection: str = "collection1"
    api_key: str = "1234567890"
    api_key_name: str = "API-KEY"
    test_env: bool = False