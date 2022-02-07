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

class BGPNeighbor_data(BaseModel):
    unicast: Optional[bool] = False
    vpnv4: Optional[bool] = False
    vrf_name: Optional[str]
    bgp_neighbor_addr: str
    bgp_remote_asn: int
    bgp_source_loopback: Optional[str]
    
class BGPData(BaseModel):
    bgp_local_asn: int
    bgp_router_id: str
    neighbor_data: Optional[List[BGPNeighbor_data]] = None
    
class config_data(BaseModel):
    connection_data: connectionData
    mpbgp_data: Optional[BGPData]



@router.post("/mpls/l3vpn/mpbgp-config/", tags=["mpbgp config"])
async def mpbgp_config(request:config_data):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
    print(req)
    connection_data = req.get('connection_data')
    mpbgp_data = req.get('mpbgp_data')
    
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
        
    template = "mp_bgp.xml"

    file_loader = FileSystemLoader("dependencies/xml_templates/")
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    mpbgp_payload = template.render(data=mpbgp_data)

    print(mpbgp_payload)   

    # Send NETCONF <edit-config>
    # try:
    with ncc_connection.locked(target='candidate'):

        ncc_connection.edit_config(mpbgp_payload, target="candidate")
        ncc_connection.commit()
        ncc.save_config(ncc_connection)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"",
            "data": "BGP successfully configured"
        }),
    )


