import logging
import datetime
#from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
import smimeX509validation
import smimeX509validation.truststore
import json
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder

class fileView(object):
    def __init__(self,anchor,fileRaw,MatchMetadata):
        self.log = logging.getLogger("fileView")
        self.anchor = anchor
        self.data = fileRaw
        self.errorNo = 0
        self.vmilist = None
        self.MatchMetadata = MatchMetadata
        self.Json = None
        self.checkmessage()
        
        
    def checkmessage(self):
        # hello
        #print str(self.MatchMetadata)
        now = datetime.datetime.utcnow()
        smimeProcessor =  smimeX509validation.smimeX509validation(self.anchor)
        try:
            smimeProcessor.Process(str(self.data))
        except smimeX509validation.truststore.TrustStoreError,E:
            self.log.error(E)
            # Error code - failed to validate image list.
            self.errorNo =  11
            return
        except smimeX509validation.smimeX509ValidationError,E:
            self.log.error(E)
            # Error code - failed to validate image list.
            self.errorNo =  11
            return
        if not smimeProcessor.verified:
            self.log.error("Failed to validate text for '%s' produced error '%s'" % (subscriptionKey,E))
            self.errorNo =  11
            return
        data = smimeProcessor.InputDaraStringIO.getvalue()
        self.subject = smimeProcessor.InputCertMetaDataList[0]['subject']
        self.issuer = smimeProcessor.InputCertMetaDataList[0]['issuer']
        jsonData = json.loads(data)
        if jsonData == None:
            self.log.error("Downlaoded metadata from '%s' was not valid JSON." % (subscriptionKey))
            self.errorNo =  37
            return
        vmilist = VMimageListDecoder(jsonData)
        if vmilist == None:
            self.log.error("Downlaoded metadata from '%s' was not valid image list Object." % (subscriptionKey))
            self.errorNo =  38
            return
        self.vmilist = vmilist
        if vmilist.endorser.metadata[u'hv:dn'] != self.subject:
            self.log.error("Endorser DN does not match signature for '%s'" (self.MatchMetadata[u'dc:identifier']))
            self.log.info("Expected DN '%s'" % (vmilist.endorser.metadata[u'hv:dn']))
            self.log.info("Downloaded DN '%s'" % (self.subject))
            # Error code - metadata and certificate dont match.
            self.errorNo =  12
            return
        if vmilist.endorser.metadata[u'hv:ca'] != self.issuer:
            self.log.error("list hv:ca does not match signature for '%s'" % (self.MatchMetadata[u'dc:identifier']))
            self.log.info("Expected CA '%s'" % (vmilist.endorser.metadata[u'hv:ca']))
            self.log.info("Downloaded CA '%s'" % (self.issuer))
            # Error code - metadata and certificate dont match.
            self.errorNo =  12
            return
            
        if vmilist.metadata[u'hv:uri'] != self.MatchMetadata[u'hv:uri']:
            self.log.error("list hv:uri does not match subscription uri for '%s'" % (self.MatchMetadata[u'dc:identifier']))
            self.log.info("Expected URI '%s'" % (subscription.uri))
            self.log.info("Downloaded URI '%s'" % (vmilist.metadata[u'hv:uri']))
            # Error code - metadata and certificate dont match.
            self.errorNo =  12
            return
        
        if vmilist.metadata[u'dc:identifier'] != self.MatchMetadata[u'dc:identifier']:
            self.log.info("Expected identifier '%s'" % (self.MatchMetadata[u'dc:identifier']))
            self.log.info("Downloaded identifier '%s'" % (vmilist.metadata[u'dc:identifier']))
            # Error code - imagelist dc:identifier invalid.
            self.errorNo =  31
            return
        now = datetime.datetime.utcnow()
        if now < vmilist.metadata[u'dc:date:created']:
            self.log.error("Image list '%s' has an invalid creation date as in the future." % (self.MatchMetadata[u'dc:identifier']))
            self.errorNo =  33
            return
        if now > vmilist.metadata[u'dc:date:expires']:
            self.log.warning("Downloaded image list '%s' has expired." % (self.MatchMetadata[u'dc:identifier']))
            self.errorNo =  34
            return
        self.vmilist = vmilist
        self.errorNo = 0
        self.Json = jsonData
        return
