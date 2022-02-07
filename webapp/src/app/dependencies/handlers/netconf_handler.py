
from dependencies.handlers.base_handler import BaseHandler
from ncclient import manager, xml_


class NetconfHandler(BaseHandler):
    def __init__(self, hostname, port, device_type, username, password) -> None:
        
        """Connection handler construction 

        Args:
            hostname (str): address/name of the device
            args : ['username', 
                    'password', 
                    'device_type', 
                    'port']
        """
        super().__init__(hostname, port, device_type, username, password)
        self.net_connect = None
        
    def connection(self):
        
        """
        Establishes netconf connection to the target device
        """
        
        connection_data = {
            "host" : self.hostname,
            "port":self.port,
            "username":self.username,
            "password":self.password,
            "hostkey_verify":False,
            "device_params" : {"name": self.device_type},
            "timeout" : 10,
        }

        NCConnection = manager.connect(**connection_data)
        return NCConnection

    def disconnect(self):
        if self.net_connect:
            self.net_connect.close_session()

    def save_config(self, nc_manager):
        
        # Build "save" XML Payload for the RPC
        save_body = ("<cisco-ia:save-config xmlns:cisco-ia='http://cisco.com/yang/cisco-ia'/>")
        
        # Send the RPC to the Device
        nc_manager.dispatch(xml_.to_ele(save_body))
            
    def get_config(self):
        pass

    def edit_config(self):
        pass
    
    def delete_config(self):
        pass
    
    def validate_config(self):
        pass