# General libraries
import re
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

class config_data(BaseModel):
    connection_data: connectionData
    vrf_name : str
    destination_ip : str
    source_ip : str
@router.post("/mpls/l3vpn/ping_vrf/", tags=["cli verify l3vpn"])
async def get_config(request: config_data):
    
    """
    Receives request data in json format and verifys mpls underlay status and configurations

    """
    req = request.dict()
    
    try:
        connection_data = req.get('connection_data')
        ssh = CliHandler(**connection_data)
        ssh.connection()
        logger.info("\n [+] SSH Connection successfully established")
        
    except Exception as e:
        logger.warning(f"\n [+] Connection Failure: \n {e}")
        
        return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({
            "status": "failure",
            "message":"Connection Failure",
            "data": f"{e}"
        }),
        )

    vrf_name = req.get('vrf_name')
    destination_ip = req.get('destination_ip')
    source_ip = req.get('source_ip')
    
    ping_vrf_command = f"do ping vrf {vrf_name} {destination_ip} source {source_ip}"

    result = ssh.connection().send_config_set(ping_vrf_command)
    
    result2 = result.split("\n")
    
    ssh.disconnect()
    logger.info("\n [+] SSH Connection closed")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"mpls underlay verification successfully done",
            "ping_result": result2,
        }),
    )
