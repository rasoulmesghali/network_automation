# General libraries
import json
from collections import defaultdict
import logging
import os
import sys
from bcrypt import re
from loguru import logger

# Pydantic schema validation
from typing import Optional
from pydantic import BaseModel

# Fastapi General
from fastapi import Security, HTTPException, APIRouter, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Internal modules
from dependencies import *

###########
# Logging #
###########
log_level = os.environ.get("log_level","INFO")
logger.add(sys.stderr, format="{time} {level} {message}", level=log_level)

# Fastapi Router
router = APIRouter()
        
@router.post("/mpls/l3vpn/edit-config/", tags=["mpls l3vpn edit config"])
async def edit_config(request):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"",
            "data": ""
        }),
    )


