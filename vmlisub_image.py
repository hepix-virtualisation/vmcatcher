#!/usr/bin/env python
from sqlalchemy import create_engine
import hepixvmlis.databaseDefinition as model

import logging
import optparse
import smimeX509validation.loadcanamespace as loadcanamespace
import sys
from hepixvmlis.__version__ import version

from sqlalchemy.orm import sessionmaker
import hepixvmlis
import urllib2
import urllib
import json
import hashlib
import datetime
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder

class db_actions():
    
    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("vmlisub_sub.db_actions")
    

    def image_lister(self):
        outputlist = []

        subauthq = self.session.query(model.Image).\
            filter(model.Subscription.imagelist_latest == model.Imagelist.id).\
            filter(model.Subscription.authorised == True).\
            filter(model.Image.imagelist == model.Imagelist.id)
            
        for item in subauthq:
            outputlist.append("%s\t%s" % (item.identifier,  item.uri))
        
        seperator = '\n'
        return seperator.join(outputlist)



def main():
    log = logging.getLogger("vmlisub_sub.main")
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-l', '--list', action ='store_true',help='list subscriptions')
    p.add_option('-d', '--database', action ='store', help='Database Initiation string',
        default='sqlite:///tutorial.db')
    p.add_option('-c', '--cert-dir', action ='store',help='Certificate directory.', metavar='INPUTDIR',
        default='/etc/grid-security/certificates/')
    p.add_option('-i', '--uuid', action ='append',help='Select subscription', metavar='UUID')
    p.add_option('-m', '--message', action ='append',help='Export latest message from subscription', metavar='OUTPUTFILE')
    p.add_option('-j', '--json', action ='append',help='Export latest json from subscription', metavar='OUTPUTFILE')
    p.add_option('-D', '--delete', action ='store_true',help='Delete subscription', metavar='OUTPUTFILE')
    
    
    options, arguments = p.parse_args()
    anchor_needed = False
    anchor =  loadcanamespace.ViewTrustAnchor()
    actions = set([])
    subscriptions_selected = set([])
    subscription_url_list = []
    if options.list:
        actions.add('list')
    if options.uuid:
        actions.add('select')
        subscriptions_selected = set(options.uuid)
    if options.message:
        actions.add('dump')
        actions.add('message')
        dump_messages_path = set(options.message)
    if options.json:
        actions.add('dump')
        actions.add('json')
        json_messages_path = set(options.json)
    if options.delete:
        actions.add('delete')
    if len(actions) == 0:
        return
    # 1 So we have some actions to process
    
    # 1.1 Initate DB
    engine = create_engine(options.database, echo=False)
    model.init(engine)
    SessionFactory = sessionmaker(bind=engine)
    # 2 Initate CA's to manage files
    if anchor_needed:
        anchor.update_ca_list(options.cert_dir)
    # Handle actions
    if 'subscribe' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        for uri in subscription_url_list:
            db.subscribe_file(anchor,uri)         
    if 'list' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        print db.image_lister()
    if 'update' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        db.subscriptions_update(anchor)
    
    if 'delete' in actions:
        if not 'select' in actions:
            log.error('No subscriptions selected.')
        Session = SessionFactory()
        db = db_actions(Session)
        for selection_uuid in subscriptions_selected:
            db.subscriptions_delete(selection_uuid)
        Session.commit()
    if 'dump' in actions:
        if not 'select' in actions:
            log.error('No subscriptions selected.')
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
