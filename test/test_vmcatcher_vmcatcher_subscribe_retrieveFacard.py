import vmcatcher.vmcatcher_subscribe.retrieveFacard
import logging
import smimeX509validation
import unittest

class TestRetrieveFacard(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger("TestRetrieveFacard")
        self.trustAnchordirectory = "/etc/grid-security/certificates"
        
    def test_appdb(self):
        anchor = smimeX509validation.LoadDirChainOfTrust(self.trustAnchordirectory)
        foo = vmcatcher.vmcatcher_subscribe.retrieveFacard.retrieveFacard()
        foo.trustanchor = anchor
        #print ("trustanchor=%s" % (foo.trustanchor))
        uri = "https://3728760c-f6d8-403f-9926-96fa9b5d15f3:x-oauth-basic@vmcaster.appdb-dev.marie.hellasgrid.gr:443/store/software/demo.va/image.list"
        foo.uri = uri
        #print ("trustanchor=%s" % (foo.trustanchor))
        responce = foo.requestAsString()
        self.log.error("output=%s" % (foo.requestAsString()))
        # self.assertIn is not available in SL5
        self.assertTrue("code" in responce.keys())
        self.assertTrue("responce" in responce.keys())
        #raise exception
        
    
