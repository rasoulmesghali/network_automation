

class OSPF:
    
    def __init__(self, pid) -> None:
        self.process_id = pid
        self.cfg = []
        
    def definition(self):
        self.cfg.append(f'router ospf {self.process_id}')
        return self
    
    def advertise(self, prefix, mask, area_id):

        """
        This function does network advertisement
        """
        self.cfg.append(f"network {prefix} {mask} area {area_id}")
        return self
    
    def advertise_networks(self, networks):
        
        for network in networks:    
            self.advertise(network.get('prefix'), 
                           network.get('mask'),
                           network.get('area_id'),)
        return self
    
    def authentication(self, key):
        pass
    
    def build(self):
        return self.cfg