from pydantic import BaseSettings


class Settings(BaseSettings):
    
    monogodb_url: str = "mongodb://root:root@127.0.0.1:27017"
    monogodb_db: str = "db1"
