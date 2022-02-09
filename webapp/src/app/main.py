# General libraries
import os
from functools import lru_cache

# Mongodb async library
import motor.motor_asyncio

# Fastapi General
from fastapi import Depends, FastAPI, Security, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Internal modules
from config.security import api_key
from routers.mpls_api.l3vpn import edit_config as l3vpn_edit_config
from routers.mpls_api.l3vpn import get_config as l3vpn_get_config

from routers.mpls_api.l3vpn import delete_loopback
from routers.mpls_api.l3vpn import delete_vrf
from routers.mpls_api.l3vpn import delete_bgp

from routers.mpls_api.l3vpn import config_loopback 
from routers.mpls_api.l3vpn import config_mpbgp
from routers.mpls_api.l3vpn import config_vrf

from routers.general_apis import change_dry_run

from routers.mpls_api.underlay import cli_config_interface
from routers.mpls_api.underlay import cli_verify_underlay_mpls

from config.security import get_api_key
from config.log import logger
from config.fastapi_app import fastapi_app
from config import env

@lru_cache()
def get_settings():
    return env.Settings()

# Fastapi App
app = fastapi_app
app.state.logger = logger


app.include_router(l3vpn_get_config.router, dependencies=[Security(get_api_key)])
app.include_router(change_dry_run.router, dependencies=[Security(get_api_key)])

app.include_router(l3vpn_edit_config.router, dependencies=[Security(get_api_key)])
app.include_router(cli_config_interface.router, dependencies=[Security(get_api_key)])
app.include_router(cli_verify_underlay_mpls.router, dependencies=[Security(get_api_key)])

app.include_router(config_loopback.router, dependencies=[Security(get_api_key)])
app.include_router(config_mpbgp.router, dependencies=[Security(get_api_key)])
app.include_router(config_vrf.router, dependencies=[Security(get_api_key)])

app.include_router(delete_loopback.router, dependencies=[Security(get_api_key)])
app.include_router(delete_vrf.router, dependencies=[Security(get_api_key)])
app.include_router(delete_bgp.router, dependencies=[Security(get_api_key)])
@app.on_event("startup")
async def startup_db_client() -> None:

    app.mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(get_settings().monogodb_url)
    app.monogodb_db = app.mongodb_client[get_settings().monogodb_db]


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
