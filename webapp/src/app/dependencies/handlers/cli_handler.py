
from dependencies.handlers.base_handler import BaseHandler
from netmiko import ConnectHandler


class CliHandler(BaseHandler):
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
        Establishes ssh connection to the target device
        """
        
        connection_data = {
            "device_type": self.device_type,
            "host": self.hostname,
            "username": self.username,
            "password": self.password,
            "secret": self.password,
            "port": self.port,
        }

        self.net_connect = ConnectHandler(**connection_data)
        return self.net_connect

    def disconnect(self):
        if self.net_connect:
            self.net_connect.disconnect()
            