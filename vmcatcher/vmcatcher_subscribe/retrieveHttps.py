import retrieveBase
import logging
import ssl
import M2Crypto
import base64
import socket
import smimeX509validation

def Property(func):
    return property(**func())


class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
        self.port_default = 443

    @Property
    def trustanchor_needed():
        doc = "port to retrieve from"
        def fget(self):
            return True
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return locals()
    def requestAsString(self):
        output = {'code' : 0}
        if self.server == None:
            output['error'] = "undefined server"
            output['code'] = 101
            return output
        if self.port == None:
            output['error'] = "undefined port"
            output['code'] = 101
            return output
        try:
            hostcert = ssl.get_server_certificate((self.server, self.port))
        except socket.gaierror as expt:
            output['error'] = expt.strerror
            output['code'] = 404
            return output

        # create contect
        ctx = M2Crypto.SSL.Context()

        ctx.set_allow_unknown_ca(True)
        # verify peer's certificate
        #ctx.set_verify(M2Crypto.SSL.verify_peer, x509StackLen)
        con = M2Crypto.httpslib.HTTPSConnection(self.server,ssl_context=ctx)
        headers = {"User-Agent": "vmcatcher"}
        if (self.username != None) and (self.password != None):
            auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
            headers["Authorization"] = "Basic %s" % (auth)
        con.request("GET" , self.path, headers=headers)
        responce =  con.getresponse()
        httpstatus = responce.status
        if httpstatus == 200:
            output['responce'] = responce.read()
        else:
            output['error'] = responce.reason
            output['code'] = httpstatus
        return output
