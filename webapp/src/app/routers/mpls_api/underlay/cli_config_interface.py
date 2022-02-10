# General libraries
from time import time
from collections import defaultdict
import logging
import os
import sys
from bcrypt import re
from loguru import logger
from functools import lru_cache

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
from config.fastapi_app import fastapi_app as app
from config import env

@lru_cache()
def get_settings():
    return env.Settings()

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
    
    
@router.post("/interface/edit-config/", tags=["cli interface config"])
async def edit_config(request:interface_request_data, app_req:Request):
    
    """
    Receives request data in json format and configures cisco csr1000v interfaces

    """
    req = request.dict()
    
    interface = Interface(req.get('type'), req.get('number'))
    interface_cfg = interface.definition()\
                                .enable()\
                                    .ip_address(req.get('ip'), req.get('mask'))\
                                        .mpls_config()\
                                            .ospf_config(req.get('ospf_pid'), req.get('ospf_area_id'))
    commands = interface_cfg.build()
    
    if app.state.dry_run:
        response_message = "dry_run feature is enabled"
        response_data = commands
    else:
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

        result = ssh.connection().send_config_set(commands)

        ssh.disconnect()
        logger.info("\n [+] SSH Connection closed")
        
        response_message = "operation is successfully done"
        response_data = f"The interface successfully configured"
        
        # Storing data into mongodb database
        config_parameters = req
        del config_parameters['connection_data']
        storing_document = {}
        storing_document['timestamp'] = time()
        storing_document['target_host'] = connection_data.get('hostname')
        storing_document['operation'] = "edit"
        storing_document['config_parameters'] = config_parameters
        storing_document['pyload'] = commands

        try:
            await app_req.app.monogodb_db[get_settings().monogodb_collection].insert_one(storing_document)
        except Exception as e:
            logger.warning("\n [+] Mongodb connection failure, check connectiong settings")
        
            response_message = "operation is successfully done"
            response_data = f"database connection failure, however, The interface successfully configured"
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({
            "status": "success",
            "message":response_message,
            "data": response_data
        }),
    )


