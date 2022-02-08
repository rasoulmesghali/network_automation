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

class connectionData(BaseModel):
    hostname: str
    port: int
    username: str
    password: str
    device_type: str
        
class loopBackData(BaseModel):
    loopback_number: int
    ipv4: Optional[str]
    ipv4_mask: Optional[str]
    vrf_name: Optional[str] = None
    
class config_data(BaseModel):
    connection_data: connectionData
    loopback_data: Optional[loopBackData]


@router.post("/mpls/l3vpn/loopback-config/", tags=["loopback config"])
async def loopback_config(request:config_data):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """
 
    req = request.dict()
    print(req)
    connection_data = req.get('connection_data')
    loopback_data = req.get('loopback_data')
    loopback_number = loopback_data.get('loopback_number')

    template = "loopback_interface.xml"

    file_loader = FileSystemLoader("dependencies/xml_templates/")
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    loopback_payload = template.render(data=loopback_data)

    if app.state.dry_run:
        response_message = "dry_run feature is enabled"
        response_data = loopback_payload
    else:
        try:
            ncc = NetconfHandler(**connection_data)
            ncc_connection = ncc.connection()
            logger.info("\n [+] Netconf Connection successfully established")    
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

        # Send NETCONF <edit-config>
        # try:
        with ncc_connection.locked(target='candidate'):
            
            ncc_connection.edit_config(loopback_payload, target="candidate")
            ncc_connection.commit()
            ncc.save_config(ncc_connection)
        
        response_message = "operation is successfully done"
        response_data = f"The loopback {loopback_number} successfully configured"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":response_message,
            "data": response_data
        }),
    )


