# General libraries
import json
from collections import defaultdict
import logging
import os
import sys
from bcrypt import re
from loguru import logger
from typing import List
from time import time

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

BASE_DIR = os.path.abspath(os.path.join(__file__ ,"../../../../../../"))
module_path = os.path.join(BASE_DIR)
sys.path.append(module_path)

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
    vrf_name: Optional[str]
    vrf_rd: Optional[str]
    vrf_export_rt: Optional[str]
    vrf_import_rt: Optional[str]

class config_data(BaseModel):
    connection_data: connectionData
    vrf_data: Optional[VRFdata]


@router.post("/mpls/l3vpn/vrf-config/", tags=["vrf config"])
async def vrf_config(request:config_data, app_req:Request):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
    print(req)
    connection_data = req.get('connection_data')
    vrf_data = req.get('vrf_data')

    template = "vrf.xml"

    file_loader = FileSystemLoader(os.path.join(BASE_DIR,"src/app/dependencies/xml_templates/"))
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    vrf_payload = template.render(data=vrf_data)

    if app.state.dry_run:
        response_message = "dry_run feature is enabled"
        response_data = vrf_payload
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
        try:
            with ncc_connection.locked(target='candidate'):
                
                ncc_connection.edit_config(vrf_payload, target="candidate")        
                ncc_connection.commit()
                ncc.save_config(ncc_connection)

            # Storing data into mongodb database
            storing_document = {}
            storing_document['timestamp'] = time()
            storing_document['operation'] = "edit"
            storing_document['config_parameters'] = vrf_data
            storing_document['pyload'] = vrf_payload

            await app_req.app.monogodb_db.db1.insert_one(storing_document)
            
            response_message = "operation is successfully done"
            response_data = "vrf successfully created"
            
        except Exception as e:
            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({
                "status": "failure",
                "message":"The operation failed",
                "data": "Check existing vrf with similar configuration"
            }),
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":response_message,
            "data": response_data
        }),
    )


