# General libraries
import os
import asyncio
import typing
import pydantic

# Mongodb async library
import motor.motor_asyncio

# Fastapi General
import fastapi
from fastapi import Depends, FastAPI, Security, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Internal modules
from routers.mpls_api.l3vpn import edit_config as l3vpn_edit_config
from routers.mpls_api.l3vpn import get_config as l3vpn_get_config
from routers.mpls_api.l3vpn import delete_config as l3vpn_delete_config
from routers.mpls_api.underlay import edit_config as underlay_edit_config
from routers.mpls_api.underlay import get_config as underlay_get_config
from config.security import get_api_key
from config.log import logger

# Fastapi App
app = FastAPI()
app.state.logger = logger
# app.include_router(mplsapi.router, dependencies=[Security(get_api_key)])
app.include_router(l3vpn_get_config.router)
app.include_router(l3vpn_delete_config.router)
app.include_router(l3vpn_edit_config.router)
app.include_router(underlay_get_config.router)
app.include_router(underlay_edit_config.router)
@app.on_event("startup")
async def startup_db_client() -> None:

    default_mongo = "mongodb://root:root@mongodb:27017"
    app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_DB_URL", default_mongo))
    app.mongodb = app.mongodb_client[os.environ.get("MONGO_DB_NAME", "webapp")]


@app.on_event("startup")
async def show_environment_variables() -> None:

    logger.info("""
             _   _ _____ _______        _____  ____  _  __     _   _   _ _____ ___  __  __    _  _____ ___ ___  _   _ 
            | \ | | ____|_   _\ \      / / _ \|  _ \| |/ /    / \ | | | |_   _/ _ \|  \/  |  / \|_   _|_ _/ _ \| \ | |
            |  \| |  _|   | |  \ \ /\ / / | | | |_) | ' /    / _ \| | | | | || | | | |\/| | / _ \ | |  | | | | |  \| |
            | |\  | |___  | |   \ V  V /| |_| |  _ <| . \   / ___ \ |_| | | || |_| | |  | |/ ___ \| |  | | |_| | |\  |
            |_| \_|_____| |_|    \_/\_/  \___/|_| \_\_|\_\ /_/   \_\___/  |_| \___/|_|  |_/_/   \_\_| |___\___/|_| \_|
            """)
    
    logger.info("[+] Available Environment variables are as follow:")
    logger.info(f"[+] MONGO DB URL: {os.environ.get('MONGO_DB_URL')}")
    logger.info(f"[+] MONGO DB NAME: {os.environ.get('MONGO_DB_NAME')}")
    logger.info(f"[+] Log Level: {os.environ.get('log_level')}")
    logger.info(f"[+] API KEY HEADER: {os.environ.get('api_key_name')}")
    logger.info(f"[+] API KEY: {os.environ.get('api_key')}")
    
    
@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    app.mongodb_client.close()


#Custom FastAPI's exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({
            "message": exc.detail,
            "errors": exc.status_code,
            "status": "failure", 
            "data": []
        }),
    )

#Override request validation exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "message": exc.errors()[0]['msg'],
            "errors": exc.errors()[0]['type'],
            "status": "failure",
            "data": exc.errors()
        }),
    )

@app.get("/info")
async def info():
    return {
        "app_name": "Network Automation",
        "app_version": "version 0.1",
        "admin_email": "rasoul.mesghali@gmail.com",
    }
