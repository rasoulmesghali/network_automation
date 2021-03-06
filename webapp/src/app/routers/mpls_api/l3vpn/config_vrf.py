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
from functools import lru_cache
import ipaddress

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
from dependencies.helper.route_target_distinguisher_validator import validate_rt_rd

from config import env

@lru_cache()
def get_settings():
    return env.Settings()

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
    vrf_rd: Optional[str]
    vrf_export_rt: Optional[str]
    vrf_import_rt: Optional[str]

class config_data(BaseModel):
    connection_data: connectionData
    vrf_data: VRFdata


@router.post("/mpls/l3vpn/vrf-config/", tags=["vrf config"])
async def vrf_config(request:config_data, app_req:Request):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
    connection_data = req.get('connection_data')
    vrf_data = req.get('vrf_data')

    ###########################
    # Fields validation
    ############################
    if vrf_data.get("vrf_rd") == None:
        del vrf_data["vrf_rd"]
    elif vrf_data.get("vrf_rd") != None and not validate_rt_rd(vrf_data.get("vrf_rd")):
                    
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status": "failure",
                "message":"operation failure",
                "data": "wrong vrf_rd"
            }),
            )

    if vrf_data.get("vrf_export_rt") == None:
        del vrf_data["vrf_export_rt"]
    elif vrf_data.get("vrf_export_rt") != None and not validate_rt_rd(vrf_data.get("vrf_export_rt")):
                    
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status": "failure",
                "message":"operation failure",
                "data": "wrong vrf_export_rt"
            }),
            )
        
    if vrf_data.get("vrf_import_rt") == None:
        del vrf_data["vrf_import_rt"]
    elif vrf_data.get("vrf_import_rt") != None and not validate_rt_rd(vrf_data.get("vrf_import_rt")):
                    
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({
                "status": "failure",
                "message":"operation failure",
                "data": "wrong vrf_import_rt"
            }),
            )

    if app_req.app.test_env:
        BASE_DIR = os.path.abspath(os.path.join(__file__ ,"../../../../../../"))
        module_path = os.path.join(BASE_DIR)
        sys.path.append(module_path)

        template_path = os.path.join(BASE_DIR,"src/app/dependencies/xml_templates/")
    else:
        template_path = "dependencies/xml_templates/"
        
    template = "vrf.xml"

    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    vrf_payload = template.render(data=vrf_data)

    if app_req.app.state.dry_run:
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

        # Storing data into mongodb database
        storing_document = {}
        storing_document['timestamp'] = time()
        storing_document['target_host'] = connection_data.get('hostname')
        storing_document['operation'] = "edit"
        storing_document['config_parameters'] = vrf_data
        storing_document['pyload'] = vrf_payload

        try:
            await app_req.app.monogodb_db[get_settings().monogodb_collection].insert_one(storing_document)
        except Exception as e:
            logger.warning("\n [+] Mongodb connection failure, check connectiong settings")
            
            response_message = "operation is successfully done"
            response_data = "database connection failure, however, vrf successfully created"
            
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":response_message,
            "data": response_data
        }),
    )


