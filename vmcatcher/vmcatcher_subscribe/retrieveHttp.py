import retrieveBase
import logging
import httplib

import base64
timeout = 60

class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
        self.port_default = 80
        
    def requestAsString(self):
        auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
        con = httplib.HTTPConnection(self.server, self.port, True, timeout)
        headers = {"Authorization" : "Basic %s" % auth,
            "User-Agent": "vmcatcher"}
        con.request("GET" , self.path, headers=headers)
        responce =  con.getresponse()
        output = {'responce' : responce.read() }
        return output
        
