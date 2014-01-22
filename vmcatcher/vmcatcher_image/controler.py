from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import vmcatcher.databaseDefinition as model
import os
import logging
import optparse
from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
from vmcatcher.__version__ import version
import vmcatcher
import urllib2
import urllib
import hashlib
import datetime
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition
from vmcatcher.driveroutput import output_driver_lines,output_driver_smime,output_driver_message
from vmcatcher.queryby import queryby_uuid, queryby_sha512
from vmcatcher.listutils import pairsNnot
import vmcatcher.queryby
from M2Crypto import SMIME, X509, BIO
try:
    import simplejson as json
except:
    import json
import sys

class db_actions:

    def __init__(self,session):
        self.session = session
        self.log = logging.getLogger("vmcatcher_subscribe.db_actions")


    def image_lister(self):
        outputlist = []

        imageDefs = self.session.query(model.ImageDefinition,model.Subscription).\
            filter(model.Subscription.id == model.ImageDefinition.subscription)

        for q_result in imageDefs:
            imagedef = q_result[0]
            subscription = q_result[1]
            subauthq = self.session.query(model.ImageInstance,model.ImageListInstance).\
                filter(model.ImageDefinition.id == imagedef.id).\
                filter(model.Subscription.id == subscription.id).\
                filter(model.ImageDefinition.subscription == model.Subscription.id).\
                filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id).\
                filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
                filter(model.Subscription.imagelist_latest == model.ImageListInstance.id)
            bimappedOutput = imagedef.cache
            if subauthq.count() == 1:
                q_result = subauthq.one()
                imageInstance = q_result[0]
                listInstance = q_result[1]
                available = 0
                if ((imagedef.latest == imageInstance.id) and (subscription.authorised == 1) and
                    (subscription.imagelist_latest == listInstance.id) and (listInstance.expired == None) and
                    (imageInstance.fkimagelistinstance != None) and (imagedef.latest !=None)):
                    available = 1
                bimappedOutput = imagedef.cache + (available << 1)
            outputlist.append("%s\t%s\t%s" % (imagedef.identifier,bimappedOutput,subscription.identifier))

        seperator = '\n'
        return seperator.join(outputlist)

    def image_by_sha512_writefile_imagelist(self,treess,sha512,path):
        query_image = self.session.query(model.ImageInstance).\
            filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
            filter(model.ImageInstance.sha512 == str(sha512))
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        fp = open(path,'w')
        for image in query_image:
            fp.write(image.data)
        fp.close()
        return True


    def image_by_sha512_writefile_json(self,treess,sha512,path):
        query_image = self.session.query(model.ImageInstance,model.ImageListInstance).\
            filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
            filter(model.ImageInstance.sha512 == sha512)
        if query_image.count() == 0:
            self.log.warning('Message not found')
            return False
        fp = open(path,'w')
        for touple_set in query_image:
            image = touple_set[0]
            image_list = touple_set[1]
            buf = BIO.MemoryBuffer(str(image_list.data))
            sk = X509.X509_Stack()
            p7, data = SMIME.smime_load_pkcs7_bio(buf)
            data_str = data.read()
            fp.write(data_str)
        fp.close()
    def image_by_sha512_display_info(self,ancore,sha512):
        output = []
        query_image = self.session.query(model.ImageInstance,model.ImageListInstance).\
            filter(model.ImageInstance.fkimagelistinstance == model.ImageListInstance.id).\
            filter(model.ImageInstance.sha512 == str(sha512))
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


class db_controler:
    def __init__(self,dboptions, dblog):
        self.log = logging.getLogger("vmcatcher_image.controler")
        self.engine = create_engine(dboptions, echo=dblog)
        model.init(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.anchor = None
        self.selector_curent = None
        self.selectors_available = ['image_uuid','image_sha512']
    def setup_trust_anchor(self,directory):
        self.anchor = LoadDirChainOfTrust(directory)

    def set_selector(self,selector_string):
        self.selector_curent = None
        if not selector_string in self.selectors_available:
            self.log.warning("Invalid selector string set:%s" % (selector_string))
            return False
        if selector_string == 'image_uuid':
            self.selector_curent = vmcatcher.queryby.query_imageDef_by_identifier
        elif selector_string == 'image_sha512':
            self.selector_curent = vmcatcher.queryby.query_imageDef_by_sha512
        return True
        
    def setup_view_factory(self,factory):
        self.factory_view = factory
    def images_info(self,images_selected,outputfiles):
        pairs, extra_selectors ,extra_paths = pairsNnot(images_selected,outputfiles)

        for item in extra_selectors:
            pairs.append([item,None])

        NoErrorHappened = True
        Session = self.SessionFactory()
        
        for pair in pairs:
            selector_filter = pair[0]
            output_file_name = pair[1]
            output_fileptr = sys.stdout
            if output_file_name != None:
                output_fileptr = open(output_file_name,'w+')
                output_fileptr.flush()

            queryImageDef = self.selector_curent(Session, selector_filter)
            if queryImageDef.count() == 0:
                self.log.warning("Selections '%s' does not match any known images." % (selector_filter))
                continue
            view = self.factory_view(output_fileptr,Session,self.anchor)
            for imagedef in queryImageDef:
                details = Session.query(model.ImageListInstance,model.ImageInstance).\
                    filter(model.ImageListInstance.id==model.ImageInstance.fkimagelistinstance).\
                    filter(model.ImageDefinition.id == imagedef.id).\
                    filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id).\
                    filter(model.Subscription.id == imagedef.subscription).\
                    filter(model.Subscription.imagelist_latest == model.ImageListInstance.id)
                if details.count() == 0:
                    self.log.warning("Image '%s' has expired." % (selector_filter))
                for item in details:
                    imagelist = item[0]
                    image = item[1]
                    if not view.display_imagelistImage(imagedef,imagelist,image):
                        NoErrorHappened = False
            if output_file_name != None:
                output_fileptr.close()
        return NoErrorHappened

    def image_list(self):
        Session = self.SessionFactory()
        db = db_actions(Session)
        print db.image_lister()
    def images_subscribe(self,images_selected,subscribe):
        Session = self.SessionFactory()
        
        for image in images_selected:
            queryImageDef = self.selector_curent(Session, image)
            for ImageDef in queryImageDef:
                ImageDef.cache = subscribe
                Session.add(ImageDef)
                Session.commit()
