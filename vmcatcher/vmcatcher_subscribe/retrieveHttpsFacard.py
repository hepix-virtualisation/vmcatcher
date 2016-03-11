import retrieveBase
import logging
import retrieveHttps
import retrieveHttpsIgtfTa
import retrieveFacard

def Property(func):
    return property(**func())


class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
        self.port_default = 443
        self.log = logging.getLogger("uploaderHttpsFacade")
        self._retrieveImp = None
        # Detailed properties
        self.server = kwargs.get('server', None)
        self.port = kwargs.get('port', None)
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        self.path = kwargs.get('path', None)
        self.trustanchor = kwargs.get('trustanchor', None)
        self.trustanchor_needed = kwargs.get('trustanchor_needed', None)
        self.trustanchor_type = kwargs.get('trustanchor_type',retrieveFacard.TRUST_ANCHOR_NONE)
        # Set implementation
        self.uri = kwargs.get('uri', None)

    @Property
    def trustanchor_type():
        doc = "trustanchor_type to verify hosts against"
        def fget(self):
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    if hasattr(self._retrieveImp,'trustanchor_needed'):
                        return self._retrieveImp._trustanchor_type
                    else:
                        return None
            return self._trustanchor_type

        def fset(self, value):
            self._trustanchor_type = value
            if not value in [retrieveFacard.TRUST_ANCHOR_NONE,
                retrieveFacard.TRUST_ANCHOR_BROWSER,
                 retrieveFacard.TRUST_ANCHOR_IGTF]:
                raise retrieveFacardError("Invalid trustanchor_type='%s'" % (value))
            retrieveImpTmp = None
            if self.trustanchor_type == retrieveFacard.TRUST_ANCHOR_NONE:
                retrieveImpTmp = retrieveHttps.retrieve()
            elif self.trustanchor_type == retrieveFacard.TRUST_ANCHOR_BROWSER:
                self.log.warning("TRUST_ANCHOR_BROWSER selected but not yet implemented.")
                retrieveImpTmp = retrieveHttps.retrieve()
            elif self.trustanchor_type == retrieveFacard.TRUST_ANCHOR_IGTF:
                retrieveImpTmp = retrieveHttpsIgtfTa.retrieve()
            elif self.trustanchor_type == None:
                pass
            else:
                self.log.error("Invalid trustanchor_type selected '%s'" % (name))
            if retrieveImpTmp != None:
                retrieveImpTmp.server = self._server
                retrieveImpTmp.port = self._port
                retrieveImpTmp.username = self._username
                retrieveImpTmp.password = self._password
                retrieveImpTmp.path = self._path
                retrieveImpTmp.trustanchor = self._trustanchor
                retrieveImpTmp.trustanchor_needed = self._trustanchor_needed
                retrieveImpTmp.trustanchor_type = self._trustanchor_type
                retrieveImpTmp.protocol = "https"
                self._retrieveImp = retrieveImpTmp
            else:
                if hasattr(self, '_retrieveImp'):
                    del(retrieveImpTmp)
            self._trustanchor_type = value
            if hasattr(self, '_retrieveImp'):
                if self._retrieveImp != None:
                    self._retrieveImp._trustanchor_type = value
        def fdel(self):
            del self._trustanchor_type
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

    def requestAsString(self):
        if hasattr(self, '_retrieveImp'):
            if self._retrieveImp != None:
                return self._retrieveImp.requestAsString()
            else:
                self.log.critical("programming error no protocol is None")
        else:
            self.log.critical("programming error no protocol implementation")
        return None

