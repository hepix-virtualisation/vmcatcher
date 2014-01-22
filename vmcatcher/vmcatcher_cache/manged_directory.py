import urlparse
import os
import os.path
import shutil
import logging
import json

def uglyUriParser(uri):
    parsedUri = urlparse.urlsplit(uri)
    if isinstance(parsedUri, tuple):
        # We are probably python 2.4
        networklocation = parsedUri[1].split(':')
        hostname = networklocation[0]
        port = ""
        if len (networklocation) > 1:
            port = networklocation[1]
        return { "scheme" : parsedUri[0],
            "path" : parsedUri[2],
            "hostname" : hostname,
            "port" : port,
        }
    if isinstance(parsedUri,urlparse.SplitResult):
        # We are probably python 2.6
        return { "scheme" : parsedUri.scheme,
            "path" : parsedUri.path,
            "hostname" : parsedUri.hostname,
            "port" : parsedUri.port,
        }
        

class BaseDir(object):
    def __init__(self, directory):
        self.directory = directory
        self.indexFile = "cache.index"
        self.index = {}
        self.indexLoad()
        # self.files = { 'uuid' : { 'sha512' : 'hash', 'message' : 'signed message' , 'date' : }
        self.indexUnknownClear()
        self.log = logging.getLogger("BaseDir")
 
        
    def getFiles(self):
        output = set()
        directoryList = os.listdir(self.directory)
        for item in directoryList:
            if item == self.indexFile:
                continue
            filepath = os.path.join(self.directory,item)
            if os.path.isfile(filepath):
                output.add(item)
        return output

    def indexLoad(self):
        indexFilePath = os.path.join(self.directory,self.indexFile)
        if os.path.isfile(indexFilePath):
            fp = open(indexFilePath,'r')
            lines = fp.read()
            tmp = json.loads(lines)
            if type(tmp) is dict:
                self.index = tmp
        return True

    def indexSave(self):
        self.indexUnknownClear()
        indexFilePath = os.path.join(self.directory,self.indexFile)
        fp = open(indexFilePath,'w')
        fp.write(json.dumps(self.index,sort_keys=True, indent=4))
        fp.flush()
        fp.close()
        return True

    def indexUnknownClear(self):
        allfiles = self.getFiles()
        for filename in allfiles:
            unknown = True
            for uuid in self.index.keys():
                if 'filename' in self.index[uuid].keys():
                    if self.index[uuid]['filename'] == filename:
                        unknown = False
            if unknown:
                filepath = os.path.join(self.directory,filename)
                os.remove(filepath)
    def indexAdd(self,metadata):
        requiredkeys = set(['uuid','sha512','uri','size'])
        metadataKeys = set(metadata.keys())
        if not requiredkeys.issubset(metadataKeys):
            return False
        uuid = metadata['uuid']
        if not uuid in self.index.keys():
            self.index[uuid] = dict(metadata)
            return True
        self.index[uuid].update(metadata)
        return True
    def moveFrom(self,aDir,uuid):
        if not isinstance(aDir,BaseDir):
            self.log.error("not a BaseDir object code error")
            return False
        if not uuid in aDir.index.keys():
            self.log.error("uuid '%s' is not in directory %s" % (aDir, self.directory))
            return False
        origin = os.path.join(aDir.directory,aDir.index[uuid]['filename'])
        destination = os.path.join(self.directory,uuid)
        shutil.move(origin, destination)
        self.index[uuid] = aDir.index[uuid]
        self.index[uuid]['filename'] = uuid
        del aDir.index[uuid]
        return True

class DownloadDir(BaseDir):
    def __init__(self, dir_download):
        BaseDir.__init__(self,dir_download)
        self.log = logging.getLogger("DownloadDir")

    def download(self,uuid):
        if not uuid in self.index.keys():
            self.log.error("Image '%s' is not known" % (uuid))
            return False
        DownLoadTrys = 0
        if u'DownLoadTrys' in self.index[uuid].keys():
            if 'msgHash' in self.index[uuid]['DownLoadTrys'].keys():
                if self.index[uuid]['DownLoadTrys']['msgHash'] == self.index[uuid]['msgHash']:
                    DownLoadTrys = int(self.index[uuid]['DownLoadTrys']['count'])
        if DownLoadTrys >= 5:
            self.log.warning("Image '%s' has failed to download '%s' times, giving up until new image list." % (uuid,DownLoadTrys))
            return False
        self.index[uuid]['DownLoadTrys'] = { 'count' : DownLoadTrys + 1 , 'msgHash' : self.index[uuid]['msgHash'] }
        self.index[uuid]['filename'] = uuid
        self.indexSave()
        if self.index[uuid]['size'] != None:
            stats = os.statvfs(self.directory)
            diskspace = (stats[statvfs.F_BSIZE] * stats[statvfs.F_BAVAIL])
            imagesize = self.index[uuid]['size']
            if imagesize > diskspace:
                self.log.error("Image '%s' is too large at '%s' bytes, available disk space is '%s' bytes." % (uuid,imagesize,diskspace))
                return False
        self.log.info("Downloading '%s'." % (uuid))
        filepath = os.path.join(self.directory,self.index[uuid]['filename'])
        uriParsed = uglyUriParser(self.index[uuid]['uri'])
        unknownTransport = True
        if uriParsed['scheme'] == u'http':
            cmd = "wget -q -O %s %s" % (filepath,self.index[uuid]['uri'])
            rc,output = commands.getstatusoutput(cmd)
            if rc != 0:
                self.log.error("Command '%s' failed with return code '%s' for image '%s'" % (cmd,rc,uuid))
                if len(output) > 0:
                    self.log.info("Output '%s'" % (output))
                os.remove(filepath)
                return False
            unknownTransport = False
        if uriParsed['scheme'] == u'https':
            cmd = "wget -q -O %s %s --no-check-certificate" % (filepath,self.index[uuid]['uri'])
            rc,output = commands.getstatusoutput(cmd)
            if rc != 0:
                self.log.error("Command '%s' failed with return code '%s' for image '%s'" % (cmd,rc,uuid))
                if len(output) > 0:
                    self.log.info("Output '%s'" % (output))
                os.remove(filepath)
                return False
            unknownTransport = False
        if uriParsed['scheme'] == u'file':
            shutil.copyfile(uriParsed['path'],filepath)
            unknownTransport = False
        if unknownTransport:
            self.log.error("Unknown transport '%s' for URI for '%s'" % (uriParsed['scheme'],uuid))
            return False
        file_metadata = file_extract_metadata(filepath)
        if file_metadata == None:
            self.log.error("Failed to get metadata for image '%s' at path '%s'." % (uuid,filepath))
            return False
        if file_metadata[u'sl:checksum:sha512'] != self.index[uuid]['sha512']:
            os.remove(filepath)
            self.log.error("Downloaded image '%s' has unexpected sha512." % (uuid))
            self.log.info("Expected sha512 '%s'" % (self.index[uuid]['sha512']))
            self.log.info("Downloaded sha512 '%s'" % (file_metadata[u'sl:checksum:sha512']))
            return False
        if self.index[uuid]['size'] != None:
            if int(file_metadata[u'hv:size']) != int(self.index[uuid]['size']):
                os.remove(filepath)
                self.log.error("Image '%s' is incorrect size." % (uuid))
                return False
        return True

class CacheDir(BaseDir):
    def __init__(self, dir_cache):
        BaseDir.__init__(self,dir_cache)
        self.log = logging.getLogger("CacheDir")
    def getExpired(self,validDict):
        # Takes a dictionary of uuid : sha512 mappings.
        # Returns the file path of all files not matching
        pass

class ExpireDir(BaseDir):
    def __init__(self, dir_cache):
        BaseDir.__init__(self,dir_cache)
        self.log = logging.getLogger("ExpireDir")

    def moveFrom(self,aDir,uuid):
        if not isinstance(aDir,BaseDir):
            self.log.error("not a BaseDir object code error")
            return False
        if not uuid in aDir.index.keys():
            self.log.error("uuid '%s' is not in directory %s" % aDir)
            return False
        idStr = "%s.%s" % (uuid, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        origin = os.path.join(aDir.directory,aDir.index[uuid]['filename'])
        if not os.path.isfile(origin):
            self.log.error("uuid '%s' referances file '%s' but file does not exist." % (uuid,origin))
            del aDir.index[uuid]
            return False
        destination = os.path.join(self.directory,idStr)
        shutil.move(origin, destination)
        self.index[idStr] = aDir.index[uuid]
        self.index[idStr]['filename'] = idStr
        del aDir.index[uuid]
        return True
