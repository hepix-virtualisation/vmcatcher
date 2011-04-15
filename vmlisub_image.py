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
from M2Crypto import SMIME, X509, BIO
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
    
    def image_by_sha512_writefile_imagelist(self,sha512,path):
        query_image = self.session.query(model.Imagelist).\
            filter(model.Image.sha512 == sha512)
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        fp = open(path,'w')
        for image in query_image:
            
            fp.write(image.data)
        fp.close()
        
    def json_message(self,sha512,path):
        query_image = self.session.query(model.Imagelist).\
            filter(model.Image.sha512 == sha512)
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        fp = open(path,'w')
        for image in query_image:
            buf = BIO.MemoryBuffer(str(image.data))
            sk = X509.X509_Stack()
            p7, data = SMIME.smime_load_pkcs7_bio(buf)
            data_str = data.read()
            fp.write(data_str)
        fp.close()
        
# User interface

def pairsNnot(list_a,list_b):
    len_generate_list = len(list_a)
    len_image_list = len(list_b)
    ocupies_generate_list = set(range(len_generate_list))
    ocupies_image_list = set(range(len_image_list))
    ocupies_pairs = ocupies_image_list.intersection(ocupies_generate_list)
    diff_a = ocupies_generate_list.difference(ocupies_image_list)
    diff_b = ocupies_image_list.difference(ocupies_generate_list)
    arepairs = []
    for i in ocupies_pairs:
        arepairs.append([list_a[i],list_b[i]])
    notpairs_a = []
    for i in diff_a:
        notpairs_a.append(list_a[i])
    notpairs_b = []
    for i in diff_b:
        notpairs_b.append(list_b[i])
    
    return arepairs,notpairs_a,notpairs_b


def main():
    log = logging.getLogger("vmlisub_sub.main")
    """Runs program and handles command line options"""
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-l', '--list', action ='store_true',help='list subscriptions')
    p.add_option('-d', '--database', action ='store', help='Database Initiation string',
        default='sqlite:///tutorial.db')
    p.add_option('-c', '--cert-dir', action ='store',help='Certificate directory.', metavar='INPUTDIR',
        default='/etc/grid-security/certificates/')
    p.add_option('--sha512', action ='append',help='Select images by identifier. Typically a UUID', metavar='UUID')
    
    p.add_option('-m', '--message', action ='append',help='Export latest message from subscription', metavar='OUTPUTFILE')
    p.add_option('-j', '--json', action ='append',help='Export latest json from subscription', metavar='OUTPUTFILE')
    p.add_option('-D', '--delete', action ='store_true',help='Delete subscription', metavar='OUTPUTFILE')
    
    
    options, arguments = p.parse_args()
    anchor_needed = False
    anchor =  loadcanamespace.ViewTrustAnchor()
    actions = set([])
    uuid_selected = []
    messages_path = []
    subscription_url_list = []
    
    if options.list:
        actions.add('list')
    if options.sha512:
        actions.add('select')
        uuid_selected = options.sha512
    if options.message:
        actions.add('dump')
        actions.add('message')
        messages_path = options.message
    if options.json:
        actions.add('dump')
        actions.add('json')
        messages_path = options.json
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
        for selection_uuid in uuid_selected:
            db.subscriptions_delete(selection_uuid)
        Session.commit()
        sys.exit(0)
    if 'dump' in actions:
        if not 'select' in actions:
            log.error('No subscriptions selected.')
        if 'json' in actions:
            pairs, extra_uuid ,extra_paths = pairsNnot(uuid_selected,messages_path)
            if len(extra_paths) > 0:
                log.warning('Extra paths will be ignored.')
                for path in extra_paths:
                    log.info('ignoring path %s' % (path))
            if len(extra_uuid) > 0:
                log.warning('sha512 ignored.')
                for path in extra_uuid:
                    log.info('ignoring sha512 %s' % (path))
            Session = SessionFactory()
            db = db_actions(Session)
            for item in pairs:
                db.json_message(item[0],item[1])
        if 'message' in actions:
            pairs, extra_uuid ,extra_paths = pairsNnot(uuid_selected,messages_path)
            if len(extra_paths) > 0:
                log.warning('Extra paths will be ignored.')
                for path in extra_paths:
                    log.info('ignoring path %s' % (path))
            if len(extra_uuid) > 0:
                log.warning('sha512 ignored.')
                for path in extra_uuid:
                    log.info('Ignoring sha512 %s' % (path))
            
            Session = SessionFactory()
            db = db_actions(Session)
            for item in pairs:
                db.image_by_sha512_writefile_imagelist(item[0],item[1])
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
