from .testPayloads import *
import json
from functools import lru_cache
from fastapi.testclient import TestClient
import os, sys
import pytest

BASE_DIR = os.path.abspath(os.path.join(__file__ ,"../../../.."))
module_path = os.path.join(BASE_DIR)
sys.path.append(module_path)

from config import env
from src.app.main import app

@lru_cache()
def get_settings():
    return env.Settings()

api_key =  get_settings().api_key

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_vrf_config_api(client):
    
    """
		This is a test for VRF configuration api.
	"""

    data = json.loads(nc_vrf_config)
    data['application_uid'] = "unknownapp_unknownapp"

    url = "/mpls/l3vpn/vrf-config/"
    
    ################################
    # API key Authentication test
    ################################
    response = client.post(
            url,
            headers = {'API-KEY': "Wrong API KEY",
                'Content-Type': 'application/json'},
            json=data,
            )
    assert response.status_code == 401

    ################################
    # API key Authentication test
    ################################
    response = client.post(
            url,
            headers = {'API-KEY': api_key,
                'Content-Type': 'application/json'},
            json=data,
            )

    assert response.status_code == 200
    
    ################################
    # Dry_run Activate test
    ################################
    
    app.state.dry_run = True
    response = client.post(
            url,
            headers = {'API-KEY': api_key,
                'Content-Type': 'application/json'},
            json=data,
            )

    assert response.status_code == 200
    assert response.json().get('message') == "dry_run feature is enabled"
    
    ################################
    # Dry_run Deactivate test
    ################################
    app.state.dry_run = False
    response = client.post(
            url,
            headers = {'API-KEY': api_key,
                'Content-Type': 'application/json'},
            json=data,
            )
    assert response.json().get('message') != "dry_run feature is enabled"
    
    ########################################
    # Target Device Wrong Credential test
    ########################################
    
    data["connection_data"]["username"] = "WrongUserName"
    app.state.dry_run = False
    response = client.post(
            url,
            headers = {'API-KEY': api_key,
                'Content-Type': 'application/json'},
            json=data,
            )
    assert response.json().get('message') == "Connection Failure"
    