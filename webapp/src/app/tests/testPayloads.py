cli_interface_config = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 22,
        "username": "admin",
        "password": "admin",
        "device_type": "cisco_xe"
        },

    "type":"loopback", 
    "number": 20, 
    "ip": "110.20.10.2", 
    "mask": "255.255.255.0",
    "enable": true,
    "mpls": true,
    "ospf": true,
    "ospf_pid": 1,
    "ospf_area_id": 1
}
"""

cli_mpls_underlay_verifications ="""
{
    "hostname": "192.168.1.6",
    "port": 22,
    "username": "admin",
    "password": "admin",
    "device_type": "cisco_xe"
}
"""

nc_vrf_delete = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },

    "vrf_name":"vpn1"
}
"""

nc_vrf_config = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },
    "vrf_data":{
        "vrf_name":"vpn1", 
        "vrf_rd": "100:1", 
        "vrf_export_rt": "100:1",
        "vrf_import_rt": "100:1"
        }
}
"""


nc_mpbgp_delete = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },
    "bgp_local_asn": 100
}
"""


nc_mpbgp_config = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },
    "mpbgp_data": {
        "bgp_local_asn": 100,
        "bgp_router_id": "1.1.1.1",
        "neighbor_data":[
            {
            "unicast":true,
            "vpnv4": true,
            "vrf_name":"vpn1", 
            "bgp_neighbor_addr": "2.2.2.2",
            "bgp_remote_asn": 100,
            "bgp_source_loopback": 0
        }]
        }
}
"""


nc_loopback_config = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },
    "loopback_data":{
        "vrf_name":"vpn1", 
        "loopback_number": 111,
        "ipv4": "110.10.10.10",
        "ipv4_mask": "255.255.255.255"
        }
}
"""

nc_loopback_delete = """
{   
    "connection_data":{
        "hostname": "192.168.1.6",
        "port": 830,
        "username": "admin",
        "password": "admin",
        "device_type": "iosxe"
        },
    "loopback_number": 111
}
"""