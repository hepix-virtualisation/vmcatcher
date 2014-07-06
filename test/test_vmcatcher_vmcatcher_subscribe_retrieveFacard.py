import vmcatcher.vmcatcher_subscribe.retrieveFacard
import logging
import smimeX509validation
import unittest

class TestRetrieveFacard(unittest.TestCase):
    def test_appdb(self):
        directory= "/etc/grid-security/certificates"
        anchor = smimeX509validation.LoadDirChainOfTrust(directory)

        foo = vmcatcher.vmcatcher_subscribe.retrieveFacard.retrieveFacard()
        print anchor
        foo.trustanchor = anchor
        print foo.trustanchor
        print ("trustanchor=%s" % (foo.trustanchor))
        uri = "https://3728760c-f6d8-403f-9926-96fa9b5d15f3:x-oauth-basic@vmcaster.appdb-dev.marie.hellasgrid.gr:443/store/software/demo.va/image.list"
        foo.uri = uri
        print ("trustanchor=%s" % (foo.trustanchor))
        print ("outpout=%s" % (foo.requestAsString()))
        uri = "https://cernvm.cern.ch/releases/image.list"
        foo.uri = uri
        #print ("outpout=%s" % (foo.requestAsString()))

    
