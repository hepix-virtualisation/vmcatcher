
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import vmcatcher.databaseDefinition as model
import os.path
import logging
import optparse
from vmcatcher.__version__ import version
import vmcatcher
import urllib2
import urllib
import hashlib
import datetime
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition
from hepixvmitrust.vmitrustlib import file_extract_metadata as file_extract_metadata
import os, statvfs
import shutil
import commands
import uuid
from M2Crypto import  BIO, SMIME, X509
try:
    import simplejson as json
except:
    import json

import urlparse
import subprocess
import time
from vmcatcher.vmcatcher_cache.manged_directory import BaseDir, DownloadDir, CacheDir, ExpireDir
from vmcatcher.launch import EventObj




class CacheMan(object):
    def __init__(self,database,dblog ,dir_cache, dir_partial, dir_expired):
        self.log = logging.getLogger("CacheMan")
        self.engine = create_engine(database, echo=dblog)
        model.init(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = self.SessionFactory()
        self.cacheDir = CacheDir(dir_cache)
        self.DownloadDir = DownloadDir(dir_partial)
        self.ExpireDir = ExpireDir(dir_expired)
        self.callbackEventExpirePrefix = None
        self.callbackEventExpirePostfix = None
        self.callbackEventAvailablePrefix = None
        self.callbackEventAvailablePostfix = None

    def checkSumCache(self):
        self.cacheDir.indexUnknownClear()
        uuid2del = set()
        for uuid in self.cacheDir.index.keys():
            filename = self.cacheDir.index[uuid]['filename']
            filepath = os.path.join(self.cacheDir.directory,filename)
            file_metadata = file_extract_metadata(filepath)
            if file_metadata == None:
                uuid2del.add(uuid)
                continue
            MatchingUuid = None
            if int(file_metadata[u'hv:size']) != int(self.cacheDir.index[uuid]['size']):
                self.log.error("Image '%s' size incorrect." % (uuid))
                uuid2del.add(uuid)
                continue
            if file_metadata[u'sl:checksum:sha512'] != self.cacheDir.index[uuid]['sha512']:
                self.log.error("Image '%s' sha512 incorrect." % (uuid))
                uuid2del.add(uuid)
                continue
        # Now we remove files that have been corrupted
        for uuid in uuid2del:
            if 'filename' in self.cacheDir.index[uuid]:
                filepath = os.path.join(self.cacheDir.directory,self.cacheDir.index[uuid]['filename'])
                if os.path.isfile(filepath):
                    os.remove(filepath)
                self.log.error("Image '%s' was corrupted deleting." % (uuid))
            del self.cacheDir.index[uuid]
        return True
    def expire(self):
        rc = True
        self.cacheDir.indexUnknownClear()
        uuids2expire = {}
        for key in self.cacheDir.index.keys():
            uuid = self.cacheDir.index[key]['uuid']
            CachedSha512 = self.cacheDir.index[key]['sha512']
            QueryResults = self.Session.query(model.Subscription,model.ImageDefinition,model.ImageListInstance,model.ImageInstance).\
                filter(model.ImageInstance.sha512 == CachedSha512).\
                filter(model.ImageDefinition.cache == 1).\
                filter(model.ImageDefinition.identifier == uuid).\
                filter(model.ImageDefinition.latest == model.ImageInstance.id).\
                filter(model.ImageDefinition.id == model.ImageInstance.fkIdentifier).\
                filter(model.Subscription.authorised == True).\
                filter(model.Subscription.imagelist_latest == model.ImageListInstance.id).\
                filter(model.ImageDefinition.subscription == model.Subscription.id).\
                filter(model.ImageListInstance.expired == None).\
                filter(model.ImageListInstance.id == model.ImageInstance.fkimagelistinstance)
            if QueryResults.count() != 1:
                uuids2expire[uuid] = self.cacheDir.index[key]
                continue
            dbSub, sbImageDef, DbImageListInst, DbImageInst = QueryResults.one()
            # If the image hash has changed expire old image
            if self.cacheDir.index[key][u'sha512'] != DbImageInst.sha512:
                uuids2expire[uuid] = self.cacheDir.index[key]
                continue
            # Is the size has changed expire old image
            if self.cacheDir.index[key][u'size'] != DbImageInst.size:
                uuids2expire[uuid] = self.cacheDir.index[key]
                continue
            # If the Image list instance has changed then update
            # Image list instance metadata from DB.
            if DbImageListInst.data_hash != self.cacheDir.index[uuid]['msgHash']:
                self.cacheDir.index[key]['message'] = DbImageListInst.data
                self.cacheDir.index[key]['msgHash'] = DbImageListInst.data_hash
        for uuid in uuids2expire.keys():
            if self.callbackEventExpirePrefix != None:
                self.callbackEventExpirePrefix(uuids2expire[uuid])
            if self.ExpireDir.moveFrom(self.cacheDir,uuid):
                self.log.info("Expired image '%s'" % (uuid))
            else:
                self.log.error("Failed to move file %s to expired directory" % (uuid))
                rc = False
            self.cacheDir.indexSave()
            self.ExpireDir.indexSave()
            if self.callbackEventExpirePostfix != None:
                self.callbackEventExpirePostfix(uuids2expire[uuid])
        return rc
    def download(self):
        downloadsneeded = {}
        QueryResults = self.Session.query(model.Subscription,model.ImageDefinition,model.ImageListInstance,model.ImageInstance).\
                filter(model.ImageDefinition.cache == 1).\
                filter(model.ImageDefinition.latest == model.ImageInstance.id).\
                filter(model.ImageDefinition.id == model.ImageInstance.fkIdentifier).\
                filter(model.ImageListInstance.expired == None).\
                filter(model.Subscription.authorised == True).\
                filter(model.Subscription.imagelist_latest == model.ImageListInstance.id).\
                filter(model.ImageDefinition.subscription == model.Subscription.id).\
                filter(model.ImageListInstance.id == model.ImageInstance.fkimagelistinstance)
        for line in QueryResults:
            sub = line[0]
            imageDef = line[1]
            imageListInst = line[2]
            ImageInst = line[3]
            uuid = imageDef.identifier

            details = {'hv:uri' : str(ImageInst.uri),
                    'sl:checksum:sha512' : str(ImageInst.sha512),
                    'hv:size': int(ImageInst.size),
                    'dc:identifier' : uuid,
                    'message' : str(imageListInst.data),
                    'hv:imagelist.dc:identifier' : str(sub.identifier),
                    'msgHash' : str(imageListInst.data_hash),
                    'dc:title' : str(ImageInst.title),
                    'dc:description' : str(ImageInst.description),
                    'hv:version' : str(ImageInst.version),
                    'hv:hypervisor' : str(ImageInst.hypervisor),
                    'sl:arch' : str(ImageInst.arch),
                    'sl:comments' : str(ImageInst.comments),
                    'sl:os' : str(ImageInst.os),
                    'sl:osversion' : str(ImageInst.osversion),
                    # And now the legacy values
                    'uri' : str(ImageInst.uri),
                    'sha512' : str(ImageInst.sha512),
                    'size': int(ImageInst.size),
                    'uuid' : uuid,
                    }


            # read message

            buf = BIO.MemoryBuffer(str(imageListInst.data))
            sk = X509.X509_Stack()
            p7, data = SMIME.smime_load_pkcs7_bio(buf)
            data_str = data.read()

            try:
                jsonData = json.loads(str(data_str))
            except ValueError:
                self.log.error("proiblem reading JSON")
                continue
            if jsonData == None:
                self.log.error("Downlaoded jsonData was not valid image.")
                continue
            vmilist = VMimageListDecoder(jsonData)
            if vmilist == None:
                self.log.error("Downlaoded metadata from '%s' was not valid image list Object." % (subscriptionKey))
            # For Vo handling
            imagelist_vo = vmilist.metadata.get(u'ad:vo')
            if imagelist_vo != None:
                if len(imagelist_vo) > 0:
                    details['hv:imagelist.ad:vo'] = imagelist_vo
            matchingImage = None
            for image in vmilist.images:
                if "dc:identifier" in image.metadata.keys():
                    if uuid == image.metadata["dc:identifier"]:
                        matchingImage = image

            if matchingImage != None:
                for metafield in matchingImage.metadata.keys():
                    newfield = "hv:image.%s" % (metafield)
                    details[newfield] = matchingImage.metadata[metafield]

            if not uuid in self.cacheDir.index.keys():
                downloadsneeded[uuid] = details
                continue
            if self.cacheDir.index[uuid]['sha512'] != str(ImageInst.sha512):
                downloadsneeded[uuid] = details
                continue
        for key in downloadsneeded.keys():
            if not self.DownloadDir.indexAdd(downloadsneeded[key]):
                self.log.error("Failed to add metadata request to download file '%s'." % (key))
                continue
            if not self.DownloadDir.download(key):
                self.log.error("Failed to download file '%s'." % (key))
                self.DownloadDir.indexSave()
                continue
            if self.callbackEventAvailablePrefix != None:
                metadata = {}
                metadata.update(dict(downloadsneeded[key]))
                metadata.update(dict(self.DownloadDir.index[key]))
                #for pkey in  metadata.keys():
                #    print "%s---%s" % (pkey, metadata[pkey])
                self.callbackEventAvailablePrefix(metadata)
            if not self.cacheDir.moveFrom(self.DownloadDir,key):
                self.log.error("Failed to Move file '%s' into the enbdorsed directory." % (key))
                continue
            self.DownloadDir.indexSave()
            self.cacheDir.indexSave()
            self.log.info("moved file %s" % (key))
            if self.callbackEventAvailablePostfix != None:
                metadata = {}
                #metadata.update(dict(ddownloadsneeded[key]))
                metadata.update(dict(self.cacheDir.index[key]))
                self.callbackEventAvailablePostfix(metadata)
        return True


    def load(self):
        self.cacheDir.indexLoad()
        self.DownloadDir.indexLoad()
        self.ExpireDir.indexLoad()
    def save(self):
        self.cacheDir.indexSave()
        self.DownloadDir.indexSave()
        self.ExpireDir.indexSave()
