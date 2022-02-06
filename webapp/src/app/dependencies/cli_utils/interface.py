class Interface:
    
    def __init__(self, type, number) -> None:
        self.number = number
        self.type = type
        self.cfg = []

    def definition(self):
        self.cfg.append(f"interface {self.type}{self.number}")
        return self
        
    def enable(self):
        # self.definition()
        self.cfg.append(f"no shutdown")
        return self
        
    def disable(self):
        # self.definition()
        self.cfg.append(f"shutdown")
        return self
    
    def ip_address(self, ip, mask):
        # self.definition()
        self.cfg.append(f"ip address {ip} {mask}")
        return self
    
    def ospf_config(self, process_id, area_id):
        # self.definition()
        self.cfg.append(f"ip ospf {process_id} area {area_id}")
        return self
    
    def mpls_config(self):
        self.cfg.append(f"mpls ip")
        return self
    
    def build(self):
        return self.cfg