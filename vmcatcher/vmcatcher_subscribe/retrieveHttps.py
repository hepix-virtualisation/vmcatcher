import retrieveBase
import logging
import ssl
import M2Crypto
import base64
import socket

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
        try:
            hostcert = ssl.get_server_certificate((self.server, self.port))
        except socket.gaierror, E:
            output['error'] = E.strerror
            output['code'] = 404
            return output
        m2x509Hostcert = M2Crypto.X509.load_cert_string(hostcert)
        itemdictionary = {}
        issuer_dn = str(m2x509Hostcert.get_issuer())
        signer_dn = str(m2x509Hostcert.get_subject())
        cert_sn = str(m2x509Hostcert.get_serial_number())
        itemdictionary['subject'] = signer_dn
        itemdictionary['issuer'] = issuer_dn
        itemdictionary['serial_number'] = cert_sn

        cetlist = [itemdictionary]

        
        
        m2x509hostcertStack = self.trustanchor.GetM2CryptoX509_Stack(cetlist)
        x509Stack = []
        popedItems = m2x509hostcertStack.pop()
        while popedItems != None:
            x509Stack.append(popedItems)
            popedItems = m2x509hostcertStack.pop()
        x509StackLen = len(x509Stack)
        if x509StackLen == 0:
            output['error'] = 'Unrecognised host certificate'
            output['code'] = 50
            return output
        
        # create contect
        ctx = M2Crypto.SSL.Context()
        # create store
        store = ctx.get_cert_store()
        # fill store
        for item in x509Stack:
            store.add_x509(item)
        
        ctx.set_allow_unknown_ca(False)
        # verify peer's certificate
        ctx.set_verify(M2Crypto.SSL.verify_peer, x509StackLen)
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
