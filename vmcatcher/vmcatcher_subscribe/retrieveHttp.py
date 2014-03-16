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
        output = {'code' : 0}
        auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
        con = httplib.HTTPConnection(self.server, self.port, True, timeout)
        headers = {"User-Agent": "vmcatcher"}
        if (self.username != None) and (self.password != None):
            auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
            headers["Authorization"] = "Basic %s" % (auth)
        con.request("GET" , self.path, headers=headers)
        responce =  con.getresponse()
        httpstatus = responce.status()
        if httpstatus == 200:
            output['responce'] == responce.read()
        else:
            output['error'] = responce.reason
            output['code'] = httpstatus
        return output
        
