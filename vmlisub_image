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
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition
from M2Crypto import SMIME, X509, BIO
class db_actions():
    
    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("vmlisub_sub.db_actions")
    

    def image_lister(self):
        outputlist = []

        subauthq = self.session.query(model.Image,model.Subscription).\
            filter(model.Subscription.imagelist_latest == model.Imagelist.id).\
            filter(model.Subscription.authorised == True).\
            filter(model.Image.imagelist == model.Imagelist.id)
            
        for q_result in subauthq:
            image = q_result[0]
            subscription = q_result[1]
            
            outputlist.append("%s\t%s\t%s" % (image.identifier,subscription.uuid,image.sha512))
        
        seperator = '\n'
        return seperator.join(outputlist)
    
    def image_by_sha512_writefile_imagelist(self,treess,sha512,path):
        query_image = self.session.query(model.Image).\
            filter(model.Image.imagelist == model.Imagelist.id).\
            filter(model.Image.sha512 == str(sha512))
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        fp = open(path,'w')
        for image in query_image:
            fp.write(image.data)
        fp.close()
        return True
        
        
    def image_by_sha512_writefile_json(self,treess,sha512,path):
        query_image = self.session.query(model.Image).\
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
    def image_by_sha512_display_info(self,ancore,sha512):
        output = []
        query_image = self.session.query(model.Image,model.Imagelist).\
            filter(model.Image.imagelist == model.Imagelist.id).\
            filter(model.Image.sha512 == str(sha512))
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        for query_row in query_image:
            image = query_row[0]
            imagelist = query_row[1]
            
            print ('dc:identifier=%s' % (image.identifier))
            print ('dc:description=%s' % (image.description))
            print ('hv:hypervisor=%s' % (image.hypervisor))
            print ('sl:checksum:sha512=%s' % (image.sha512))
            print ('hv:uri=%s' % (image.uri))
            print ('sl:os=%s' % (image.os))
            print ('sl:osversion=%s' % (image.osversion ))
            print ('sl:arch=%s' % (image.arch))
            print ('hv:version=%s' % (image.version))
            print ('hv:size=%s' % (image.size))
            print ('dc:title=%s' % (image.title))
            print ('sl:comments=%s' % (image.comments))
            print ('dc:date:imported=%s' % (imagelist.imported.strftime(time_format_definition)))
            print ('dc:date:created=%s' % (imagelist.created.strftime(time_format_definition)))
            print ('dc:date:expires=%s' % (imagelist.expires.strftime(time_format_definition)))
            #validated_data = ancore.validate_text(str(image.data))
            #data = validated_data['data']
            #dn = validated_data['signer_dn']
            #ca = validated_data['issuer_dn']
        return True


def controler():
    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("vmlisub_sub.controler")

        
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
    p.add_option('-i', '--info', action ='store_true',help='Info on selected images')
    
    
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
    if options.info:
        actions.add('info')
        anchor_needed = True
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
                db.image_by_sha512_writefile_json(anchor,item[0],item[1])
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
                db.image_by_sha512_writefile_imagelist(anchor,item[0],item[1])
    if 'info' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        for item in uuid_selected:
            db.image_by_sha512_display_info(anchor,item)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
