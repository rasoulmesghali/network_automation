# General libraries
import json
from collections import defaultdict
import logging
import os
import sys
from bcrypt import re
from loguru import logger
from typing import List
import time

# Pydantic schema validation
from typing import Optional
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader

# Fastapi General
from fastapi import Security, HTTPException, APIRouter, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Internal modules
from dependencies.handlers.netconf_handler import NetconfHandler

from config.fastapi_app import fastapi_app as app

###########
# Logging #
###########
log_level = os.environ.get("log_level","INFO")
logger.add(sys.stderr, format="{time} {level} {message}", level=log_level)

# Fastapi Router
router = APIRouter()

class config_data(BaseModel):
    dry_run: bool


@router.patch("/feature/dryrun/", tags=["dryrun activate/deactivate"])
async def dryrun_config(request:config_data):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
    dry_run = req.get('dry_run')
    app.state.dry_run = dry_run
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"operation is successfully done",
            "data": f"dry_run successfully set to {dry_run}"
        }),
    )


