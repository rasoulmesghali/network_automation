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
           
class config_data(BaseModel):
    connection_data: connectionData
    loopback_number: int


@router.delete("/mpls/l3vpn/loopback-delete/", tags=["loopback delete"])
async def loopback_delete(request:config_data, app_req:Request):
    
    """
    Receives request data in json format and configures mpls l3vpn
    """

    req = request.dict()
  
    connection_data = req.get('connection_data')
    loopback_number = req.get('loopback_number')
    loopback_data = req
    loopback_data['delete'] = True

    template = "loopback_interface.xml"

    if app_req.app.test_env:
        BASE_DIR = os.path.abspath(os.path.join(__file__ ,"../../../../../../"))
        module_path = os.path.join(BASE_DIR)
        sys.path.append(module_path)

        template_path = os.path.join(BASE_DIR,"src/app/dependencies/xml_templates/")
    else:
        template_path = "dependencies/xml_templates/"
        
    file_loader = FileSystemLoader(template_path)
    env = Environment(loader=file_loader)
    template = env.get_template(template)
    loopback_payload = template.render(data=loopback_data)
    
    if app_req.app.state.dry_run:
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
        try:
            with ncc_connection.locked(target='candidate'):
                
                ncc_connection.edit_config(loopback_payload, target="candidate")
                ncc_connection.commit()
                ncc.save_config(ncc_connection)
                
                response_message = "operation is successfully done"
                response_data = f"loopback {loopback_number} successfully removed"
                
        except Exception as e:
            return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({
                "status": "failure",
                "message":"The operation failed",
                "data": f"Loopback {loopback_number} does not exist"
            }),
            )

        # Storing data into mongodb database
        storing_document = {}
        storing_document['timestamp'] = time()
        storing_document['target_host'] = connection_data.get('hostname')
        storing_document['operation'] = "delete"
        storing_document['config_parameters'] = {}
        storing_document['config_parameters']['loopback_number'] = loopback_number
        storing_document['pyload'] = loopback_payload

        try:
            await app_req.app.monogodb_db[get_settings().monogodb_collection].insert_one(storing_document)
        except Exception as e:
            logger.warning("\n [+] Mongodb connection failure, check connectiong settings")
            
            response_message = "operation is successfully done"
            response_data = f"database connection failure, however, loopback {loopback_number} successfully removed"
            
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":response_message,
            "data": response_data
        }),
    )


