import urlparse
import retrieveHttps
import retrieveHttp
import retrieveFile
import logging


def Property(func):
    return property(**func())
    
class retrieveFacard(object):
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger("uploaderFacade")
        self._retrieveImp = None
        # Detailed properties
        self.server = kwargs.get('server', None)
        self.port = kwargs.get('port', None)
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.path = kwargs.get('path', None)
        self.trustanchor = kwargs.get('trustanchor', None)
        self.trustanchor_needed = kwargs.get('trustanchor_needed', None)
        # Set implementation
        self.uri = kwargs.get('uri', None)
        self.protocol = kwargs.get('protocol', None)

    @Property
    def protocol():
        doc = "retrieve protocol"
        def fget(self):
            return self._protocol

        def fset(self, name):
            self._protocol = name
            retrieveImpTmp = None
            if name == "https":
                retrieveImpTmp = retrieveHttps.retrieve()
            elif name == "http":
                retrieveImpTmp = retrieveHttp.retrieve()
            elif name == "file":
                retrieveImpTmp = retrieveFile.retrieve()
            elif name == None:
                pass
            else:
                self.log.error("Invalid protocol selected '%s'" % (name))
            if retrieveImpTmp != None:
                retrieveImpTmp.server = self.server
                retrieveImpTmp.port = self.port
                retrieveImpTmp.username = self.username
                retrieveImpTmp.password = self.password
                retrieveImpTmp.path = self.path
                retrieveImpTmp.trustanchor = self.trustanchor
                retrieveImpTmp.trustanchor_needed = self.trustanchor_needed
                retrieveImpTmp.protocol = self.protocol
                self._retrieveImp = retrieveImpTmp
            else:
                if hasattr(self, '_retrieveImp'):
                    del(retrieveImpTmp)
        def fdel(self):
            del self._protocol
            self._retrieveImp = None
        return locals()
    
    @Property
    def server():
        doc = "server to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'server'):
                        return self._retrieveImp.server
                    else:
                        return None
            return self._server

        def fset(self, value):
            self._server = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.server = value
        def fdel(self):
            del self._server
        return locals()

    @Property
    def port():
        doc = "port to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'port'):
                        return self._retrieveImp.port
                    else:
                        return None
            return self._port

        def fset(self, value):
            if not isinstance(value, int):
                value = None
            self._port = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.port = value
        def fdel(self):
            del self._port
        return locals()

    @Property
    def username():
        doc = "username to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'username'):
                        return self._retrieveImp.username
                    else:
                        return None
            return self._username

        def fset(self, value):
            self._username = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.username = value
        def fdel(self):
            del self._username
        return locals()

    @Property
    def password():
        doc = "password to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'password'):
                        return self._retrieveImp.password
                    else:
                        return None
            return self._password

        def fset(self, value):
            self._password = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.password = value
        def fdel(self):
            del self._password
        return locals()

    @Property
    def path():
        doc = "path to retrieve from"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'path'):
                        return self._retrieveImp.path
                    else:
                        return None
            return self._path

        def fset(self, value):
            self._path = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.path = value
        def fdel(self):
            del self._path
        return locals()

    @Property
    def trustanchor():
        doc = "trustanchor to verify hosts against"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'trustanchor'):
                        return self._retrieveImp.trustanchor
                    else:
                        return None
            return self._trustanchor

        def fset(self, value):
            self._trustanchor = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.trustanchor = value
        def fdel(self):
            del self._trustanchor
        return locals()

    @Property
    def trustanchor_needed():
        doc = "trustanchor_needed to verify hosts against"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'trustanchor_needed'):
                        return self._retrieveImp.trustanchor_needed
                    else:
                        return None
            return self._trustanchor_needed

        def fset(self, value):
            self._trustanchor_needed = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp.trustanchor_needed = value
        def fdel(self):
            del self._trustanchor_needed
        return locals()

    @Property
    def uri():
        doc = """uri to use
        Conveniance function and handles uris"""
        def fget(self):
            if self.protocol == None:
                return None
            userPass = ""
            if self.username != None:
                userPass = self.username
                if self.password == None:
                    userPass = self.username
                else:
                    userPass = "%s:%s" % (self.username, self.password)
            hostPort = ""
            if self.server != None:
                if self.port == None:
                    hostPort = self.server
                else:
                    hostPort = "%s:%s" % (self.server, self.port)
            netloc = ""
            if (len(hostPort) > 0):
                if (len(userPass) > 0):
                    netloc = "%s@%s" % (userPass, hostPort)
                else:
                    netloc = hostPort
            path = ""
            if self.path != None:
                path = self.path
            output = "%s://%s%s" % (self.protocol,netloc,path)
            return output

        def fset(self, value):
            if not isinstance(value, str):
                value = ""
            parsed = urlparse.urlparse(value)
            if len(parsed.scheme) > 0:
                self.protocol = parsed.scheme
            else:
                self.protocol = None
            newServer = None
            newPort = None
            newUsername = None
            newPassword = None
            if len(parsed.netloc) > 0:
                netloc = parsed.netloc.split('@')
                hostPort = ""
                userPass = ""
                if len(netloc) == 1:
                    hostPort = netloc[0]
                if len(netloc) == 2:
                    userPass = netloc[0]
                    hostPort = netloc[1]
                if len(userPass) > 0:
                    splitUserPass = userPass.split(':')
                    newUsername = splitUserPass[0]
                    if len(splitUserPass) > 1:
                        newPassword = ':'.join([str(x) for x in splitUserPass[1:]])
                if len(hostPort) > 0:
                    splitHostPort = hostPort.split(':')
                    newServer = splitHostPort[0]
                    if len(splitHostPort) == 2:
                        asInt = int(splitHostPort[1])
                        if asInt != 0:
                            newPort = asInt
            self.server = newServer
            self.port = newPort
            self.username = newUsername
            self.password = newPassword
            if len(parsed.path) > 0:
                self.path = parsed.path
            else:
                self.path = None
        def fdel(self):
            pass
        return locals()
    
    def requestAsString(self):
        if hasattr(self, '_retrieveImp'):
            if self._retrieveImp != None:
                return self._retrieveImp.requestAsString()
            else:
                self.log.critical("programming error no protocol is None")
        else:
            self.log.critical("programming error no protocol implementation")
        return None
        
