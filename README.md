# Network Automation
## Overview

This repository contains the python codes for network configuration automation or mpls l3vpn using netconf and netmiko.

### Prerequirements
```
1- Python3.8
2- Docker and docker-compose
3- Install all require dependencies inside the requirements.txt
```

### How to setup the project

docker-compose setup:

```
1- Have 2 CSR1000v virtual machine or real device with IOSXE17 or higher version
2- docker-compose build
3- docker-compose up
```

local setup:

```
1- Create python virtual environment
2- Install all packages in requirements.txt
3- Setup local or remote mongodb server and put connection data in .env file or environment variable
4- activate virtual environment usering this command: source virtual_env_name/bin/activate
5- go to webapp/src/app path and run uvicorn main:app --reload
```