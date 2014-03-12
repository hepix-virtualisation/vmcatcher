import retrieveBase
import logging



class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
        self.port_default = 80
