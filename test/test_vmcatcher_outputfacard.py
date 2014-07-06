import vmcatcher.vmcatcher_subscribe.retrieveFacard
import logging
import smimeX509validation
import unittest

import vmcatcher.outputfacard

from vmcatcher.vmcatcher_subscribe.fatcontroler import db_controler


class TestOutputFacard(unittest.TestCase):
    def setUp(self):
        self.outputfacard = vmcatcher.outputfacard.outputFacade()
        self.outputfacard.fpOutput = "/dev/null"
        
        
        # make in memorrydb
        databaseConnectionString = 'sqlite://'
        database = db_controler(databaseConnectionString,False)
        Session = database.SessionFactory()
        
        
        self.outputfacard.saSession = Session
        self.outputfacard.format = "lines"
    
    def tearDown(self):
        pass
    def test_format_set_lines(self):
        self.outputfacard.format = "lines"

    def test_format_set_json(self):
        self.outputfacard.format = "json"

    def test_format_set_json(self):
        self.outputfacard.format = "message"

    def test_format_set_smime(self):
        self.outputfacard.format = "SMIME"

    def test_format_set_bad(self):
        def assign_bad_name():
            self.outputfacard.format = "bad"
        self.assertRaises(vmcatcher.outputfacard.outputFacadeException, assign_bad_name)

    def test_list_vmcatcher_subscribe(self):
        self.outputfacard.list_vmcatcher_subscribe()
    
    def test_list_vmcatcher_endorser_cred(self):
        self.outputfacard.list_vmcatcher_endorser_cred()
    
    def test_list_vmcatcher_endorser_link(self):
        self.outputfacard.list_vmcatcher_endorser_link()
    
    def test_list_vmcatcher_image(self):
        self.outputfacard.list_vmcatcher_image()
        
    @unittest.skip("not finsihed")
    def test_display_subscription(self):
        self.outputfacard.display_subscription("dfsdfsdf")
    @unittest.skip("not finsihed")
    def test_display_endorser(self):
        self.display_endorseroutputfacard.display_endorser("dfsdfsdf")
    @unittest.skip("not finsihed") 
    def test_display_imagedef(self):
        self.outputfacard.display_imagedef("dfsdfsdf")
    
    def test_info(self):
        self.outputfacard.info()


        
    def test_lines(self):
        pass
    def test_json(self):
        pass
    def test_smime(self):
        pass
    def test_message(self):
        pass
    
    
    
