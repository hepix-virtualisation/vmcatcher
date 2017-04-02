import sys, os
sys.path = [os.path.abspath(os.path.dirname(os.path.dirname(__file__)))] + sys.path
import vmcatcher.vmcatcher_subscribe.retrieveFacard
import logging
import smimeX509validation
import unittest
import nose

class TestRetrieveFacard(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger("TestRetrieveFacard")
        self.trustAnchordirectory = "/etc/grid-security/certificates"

    def test_http(self):
        anchor = smimeX509validation.LoadDirChainOfTrust(self.trustAnchordirectory)
        foo = vmcatcher.vmcatcher_subscribe.retrieveFacard.retrieveFacard()
        foo.trustanchor = anchor
        #uri = "http://http.fritz.box/repos/public/imagelist/yokel.imagelist.smime"'
        uri = "http://www.yokel.org/pub/software/yokel.org/imagelist/yokel.imagelist.smime"
        foo.uri = uri
        #print ("trustanchor=%s" % (foo.trustanchor))
        responce = foo.requestAsString()
        self.log.error("output=%s" % (foo.requestAsString()))
        # self.assertIn is not available in SL5
        self.assertTrue("code" in responce.keys())
        self.assertTrue("responce" in responce.keys())
        #raise exception



if __name__ == "__main__":
    logging.basicConfig()
    LoggingLevel = logging.DEBUG
    logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")
    nose.runmodule()
