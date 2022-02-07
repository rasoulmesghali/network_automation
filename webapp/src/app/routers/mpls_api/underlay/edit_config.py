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
from dependencies.cli_utils.ospf import OSPF
from dependencies.cli_utils.interface import Interface  

# Fastapi General
from fastapi import Security, HTTPException, APIRouter, Request, Response, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Internal modules
from dependencies.handlers.cli_handler import CliHandler

###########
# Logging #
###########
log_level = os.environ.get("log_level","INFO")
logger.add(sys.stderr, format="{time} {level} {message}", level=log_level)

# Fastapi Router
router = APIRouter()

class connectionData(BaseModel):
    hostname: str
    port: int
    username: str
    password: str
    device_type: str

class interface_request_data(BaseModel):
    connection_data: connectionData
    type: str = None
    number: str = None
    ip: Optional[str] = None
    mask: Optional[str] = None
    enable: Optional[str] = None
    mpls: Optional[str] = None
    ospf: Optional[str] = None
    ospf_pid: Optional[str] = None
    ospf_area_id: Optional[str] = None
    
    
@router.post("/interface/edit-config/", tags=["mpls underlay edit config"])
async def edit_config(request:interface_request_data):
    
    """
    Receives request data in json format and configures cisco csr1000v interfaces

    """
    req = request.dict()
    try:
        connection_data = req.get('connection_data')
        ssh = CliHandler(**connection_data)
        ssh.connection()
        logger.info("\n [+] SSH Connection successfully established")
        
    except Exception as e:
        logger.warning(f"\n [+] Connection Failure: \n {e}")
        exception_list = f"{e}".replace("\n\n", "$").replace("\n", "$").split('$')
        exception_list.remove("")
        
        return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({
            "status": "failure",
            "message":"Connection Failure",
            "data": exception_list
        }),
        )

    interface = Interface(req.get('type'), req.get('number'))
    interface_cfg = interface.definition()\
                                .enable()\
                                    .ip_address(req.get('ip'), req.get('mask'))\
                                        .mpls_config()\
                                            .ospf_config(req.get('ospf_pid'), req.get('ospf_area_id'))
    commands = interface_cfg.build()
    
    result = ssh.connection().send_config_set(commands)

    ssh.disconnect()
    logger.info("\n [+] SSH Connection closed")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"required commands are successfully sent",
            "data": commands
        }),
    )


