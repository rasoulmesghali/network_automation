# Network Automation
## Overview

This repository contains the python codes for network configuration automation for simple mpls l3vpn using netconf and netmiko.
FastAPI is the web framework is used to handle all APIs.

```
1- Some parts of APIs are implemented to work with Netconf/YANG to configure interface, vrf and mpbgp
2- Some parts of APIS are implemented to deal wit CLI and we have taken benefit from netmiko library for configuration and verifications
3- Requred postman collections added to work with API
```

### Prerequirements
```
1- Python3.8
2- Docker and docker-compose
3- Install all required dependencies inside the requirements.txt
```

### How to setup the project

docker-compose setup:

```
1- Have 2 CSR1000v virtual machines or real devices with IOSXE17 or higher version
2- docker-compose build (you can use makefile instead)
3- docker-compose up (you can use makefile instead)
4- Import postman collection from "postman_collections" directory
5- Turn on routers and setup ip, username, ssh, netconf, yang
6- Use correct ip, username, password and device_type in order to connect the routers
7- test APIs using postman collections and see the results
```

local setup:

```
1- Create python virtual environment
2- Install all packages in requirements.txt
3- Setup local or remote mongodb server and put connection data in .env file or environment variable
4- activate virtual environment usering this command: source virtual_env_name/bin/activate
5- go to webapp/src/app path and run uvicorn main:app --reload
6- Have 2 CSR1000v virtual machines or real devices with IOSXE17 or higher version
7- Import postman collection from "postman_collections" directory
8- Turn on routers and setup ip, username, ssh, netconf, yang
9- Use correct ip, username, password and device_type in order to connect the routers
10- test APIs using postman collections and see the results
```

### How to connect monogodb

You need to setup db and assign credentials then put them inside the environment variables or ".env" file then connect mongodb.
There are a variety of options, I uses robo3t, https://robomongo.org/download

### API Explanations
 
**"/interface/edit-config/":**
This API is used to configure an interface of the router using Netmiko which is CLI based

**"/mpls/underlay/get-config/":**
This API is used for MPLS underly verification using Netmiko which is CLI based

**"/mpls/l3vpn/ping_vrf/":**
This API is used for MPLS L3VPN verification using Netmiko which is CLI based

**"/mpls/l3vpn/vrf-delete/":**
This API is used for removing a specific VRF using NETCONG/YANG

**"/mpls/l3vpn/vrf-config/":**
This API is used for configuring a specific VRF using NETCONG/YANG

**"/mpls/l3vpn/mpbgp-delete/":**
This API is used for removing BGP configuration using NETCONG/YANG

**"/mpls/l3vpn/mpbgp-config/":**
This API is used for configuring MPBGP using NETCONG/YANG

**"/mpls/l3vpn/loopback-config/":**
This API is used for configuring a specific loopback interface using NETCONG/YANG

**"/mpls/l3vpn/loopback-delete/":**
This API is used for removing a specific loopback interface using NETCONG/YANG