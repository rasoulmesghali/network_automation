from abc import abstractmethod, ABCMeta

class BaseHandler(metaclass=ABCMeta):
    def __init__(self, hostname, port, device_type, username, password) -> None:
        
        """
        Connection handler construction 

        Args:
            hostname (str): address/name of the device
            args : ['username', 
                    'password', 
                    'secret'
                    'device_type', 
                    'port']
        """

        self.hostname = hostname
        self.port = port
        self.device_type = device_type
        self.username = username
        self.password = password
        
    @abstractmethod
    def connection(self):
        """
        This function receives connections parameters and connect to the target device
        """
        pass
    
    # @abstractmethod
    def get_config(self):
        pass
    
    # @abstractmethod
    def edit_config(self):
        pass
    
    # @abstractmethod
    def delete_config(self):
        pass
    
    @abstractmethod
    def validate_config(self):
        pass