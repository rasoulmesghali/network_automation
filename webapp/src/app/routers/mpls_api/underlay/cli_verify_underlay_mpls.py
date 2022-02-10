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
    
@router.post("/mpls/underlay/get-config/", tags=["cli verify mpls config"])
async def get_config(request: connectionData):
    
    """
    Receives request data in json format and verifys mpls underlay status and configurations

    """
    req = request.dict()
    
    try:
        connection_data = req
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

    mpls_interfaces_command = "do show mpls interfaces"

    result = ssh.connection().send_config_set(mpls_interfaces_command)

    intf_pattern = "^[lLgGeEfF]\S+[0-9]/?[0-9]*"

    regex = re.compile(intf_pattern)

    interfaces = []

    for row in result.splitlines():
        if regex.search(row):
            interfaces.append(row.split()[0])

    ldp_neighbors_command = "do show mpls ldp neighbor | include Peer LDP Ident"
    result = ssh.connection().send_config_set(ldp_neighbors_command)
    
    ip_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    lst=[]
    for row in result.splitlines():
        match = ip_pattern.search(row)
        if match:
            lst.append(match.group(0))
    
    ssh.disconnect()
    logger.info("\n [+] SSH Connection closed")
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"mpls underlay verification successfully done",
            "mpls enabled interfaces": interfaces,
            "mpls ldp neighbors": lst
        }),
    )
