
import logging
from vmcatcher.outputbase import output_driver_smime, output_driver_message, output_driver_lines, output_driver_json

availableFormats = set([ "SMIME", "message", "lines", "json"])


def Property(func):
    return property(**func())




class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class outputFacadeInputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg
        

class outputFacade(object):
    """Facade class for mulitple implementations of uploader,
    Should be robust for setting the impleemntation or attributes
    in any order."""
    def __init__(self):
        self.log = logging.getLogger("outputFacade")

    @Property
    def fpOutput():
        doc = "Ouput File Pointer"

        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'fpOutput'):
                        return self._uploaderImp.fpOutput
            return self._fpOutput

        def fset(self, name):
            self._fpOutput = name
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.fpOutput = name 
        def fdel(self):
            del self._fpOutput
        return locals()
    @Property
    def saSession():
        doc = "Ouput File Pointer"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'saSession'):
                        return self._uploaderImp.saSession
            return self._saSession

        def fset(self, name):
            self._saSession = name
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.saSession = name 
        def fdel(self):
            del self._saSession
        return locals()
    @Property
    def x509anchor():
        doc = "Ouput File Pointer"
        def fget(self):
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    if hasattr(self._uploaderImp,'x509anchor'):
                        return self._uploaderImp.x509anchor
            return self._x509anchor

        def fset(self, name):
            self._x509anchor = name
            if hasattr(self, '_uploaderImp'):
                if self._uploaderImp != None:
                    self._uploaderImp.x509anchor = name 
        def fdel(self):
            del self._x509anchor
        return locals()        
    
    @Property
    def format():
        doc = "Ouput format"
        def fget(self):
            if hasattr(self, '_outputFormatName'):
                return self._outputFormatName
            else:
                return None
        def fset(self, name):
            if not name in availableFormats:
                del(self._uploaderImp)
                del(self._outputFormatName)
                error = InputError("Invalid Value")
                raise error
            self._outputFormatName = name
            new_implementation_ptr = {'SMIME' : output_driver_smime,
                'message' : output_driver_message,
                'lines' : output_driver_lines,
                'json' :  output_driver_json,
            }
            new_implementation = new_implementation_ptr[name]()
            try:
                new_implementation.fpOutput = self.fpOutput
            except AttributeError:
                pass
            try:
                new_implementation.saSession = self.saSession
            except AttributeError:
                pass
            try:
                new_implementation.x509anchor = self.x509anchor
            except AttributeError:
                pass
            self._uploaderImp = new_implementation
            return self._outputFormatName
        def fdel(self):
            del (self._uploaderImp)
            del (self._outputFormatName)
        return locals()  
    
    
    def list_vmcatcher_subscribe(self):
        self.log.debug("list_vmcatcher_subscribe")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.list_vmcatcher_subscribe()

    def list_vmcatcher_endorser_cred(self):
        self.log.debug("list_vmcatcher_endorser_cred")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.list_vmcatcher_endorser_cred()
    def list_vmcatcher_endorser_link(self):
        self.log.debug("list_vmcatcher_endorser_link")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.list_vmcatcher_endorser_link()
    def list_vmcatcher_image(self):
        self.log.debug("list_vmcatcher_image")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.list_vmcatcher_image()
    def display_imagelistImage(self,subscription,imagedef,imagelistinstance,imageinstance):
        self.log.debug("display_imagelistImage")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.display_imagelistImage(subscription,imagedef,imagelistinstance,imageinstance)
    def display_subscription(self,item):
        self.log.debug("display_subscription")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.display_subscription(item)
    def display_subscriptionInfo(self,imagedef,imagelist,image):        
        self.log.debug("display_subscriptionInfo")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.display_subscriptionInfo(imagedef,imagelist,image)
    def display_endorser(self,endorser):
        self.log.debug("display_endorser")
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.display_endorser(endorser)
    def info(self, *args, **kwargs):
        self.log.debug("info")
        #expected_keys = ["ImageDefinition","ImageInstance",""]
        #self.env = kwargs.get('env', {})
        if not hasattr(self, '_uploaderImp'):
            error = outputFacadeInputError("Property 'format' has invalid value.")
            raise error
            
        return self._uploaderImp.info(*args, **kwargs)
