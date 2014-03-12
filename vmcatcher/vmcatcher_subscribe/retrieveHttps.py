import retrieveBase
import logging
import ssl
import M2Crypto

import base64
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
        
        hostcert = ssl.get_server_certificate((self.server, self.port))
        m2x509Hostcert = M2Crypto.X509.load_cert_string(hostcert)
        print dir(m2x509Hostcert)
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
            return False
        
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
        auth = base64.standard_b64encode("%s:%s" % (self.username, self.password))
#auth = "%s:%s" % (username, password)
        headers = {"Authorization" : "Basic %s" % auth,
            "User-Agent": "vmcatcher"}

        #con.request("GET" , path)
        #print "withoutauth:" + con.getresponse().read()
        con.request("GET" , self.path, headers=headers)
        responce =  con.getresponse()
        print responce
        print "withauth" + responce.read()
#smimeProcessor = smimeX509validation.smimeX509validation(anchor)
