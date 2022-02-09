from testPayloads import *

from fastapi.testclient import TestClient
from config.fastapi_app import fastapi_app as app

client = TestClient(app)

