# General libraries
import json
from collections import defaultdict
import logging
import os
import sys
from bcrypt import re
from loguru import logger
import time

# Pydantic schema validation
from typing import Optional
from pydantic import BaseModel

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
class VRFdata(BaseModel):
    vrf_name: str
    vrf_rd: str
    vrf_export_rt: str
    vrf_import_rt: str
    

class BGPData(BaseModel):
    bgp_local_asn: int
    bgp_router_id: str
    bgp_neighbor_addr: str
    bgp_remote_asn: int
    bgp_source_loopback: int
class loopBackData(BaseModel):
    loopback_number: int
    ipv4: str
    ipv4_mask: str
class config_data(BaseModel):
    connection_data: connectionData
    vrf_data: VRFdata
    mpbgp_data: BGPData
    loopback_data: loopBackData


@router.post("/mpls/l3vpn/edit-config/", tags=["mpls l3vpn edit config"])
async def edit_config(request:config_data):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
    connection_data = req.get('connection_data')
    vrf_data = req.get('vrf_data')
    loopback_data = req.get('loopback_data')
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
        
    # result = ncc_connection.get_config('running').data_xml
    vrf_template = open("dependencies/xml_templates/vrf.xml").read()
    vrf_payload = vrf_template.format(**vrf_data)
        
    loopback_template = open("dependencies/xml_templates/loopback_interface.xml").read()
    loopback_payload = loopback_template.format(**loopback_data, **vrf_data)
        
    mpbgp_template = open("dependencies/xml_templates/mp_bgp.xml").read()
    mpbgp_payload = mpbgp_template.format(**mpbgp_data, **vrf_data)

    # Send NETCONF <edit-config>
    # try:
    with ncc_connection.locked(target='candidate'):
        
        ncc_connection.edit_config(vrf_payload, target="candidate")
        ncc_connection.commit()

        ncc_connection.edit_config(loopback_payload, target="candidate")
        ncc_connection.commit()

        ncc_connection.edit_config(mpbgp_payload, target="candidate")
        
        ncc_connection.commit()
        ncc.save_config(ncc_connection)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":"",
            "data": loopback_payload
        }),
    )


