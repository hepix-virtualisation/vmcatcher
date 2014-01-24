
import logging

def Property(func):
    return property(**func())


availableFormats = set([ "SMIME", "message", "lines", "json"])



class output_driver_base(object):

    def __init__(self):
        self.fpOutput = None
        self.saSession = None
        self.x509anchor = None


class output_driver_smime(output_driver_base):
    def display_subscription(self,subscription):
        pass

class output_driver_message(output_driver_base):
    def display_subscription(self,subscription):
        pass

class output_driver_lines(output_driver_base):
    def subscriptions_lister(self):
        subauthq = self.session.query(model.Subscription).all()
        for item in subauthq:
            self.file_pointer.write ("%s\t%s\t%s\n" % (item.identifier,item.authorised,item.uri))


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
        self._outputFormat = None
        self._flags = None
        self.externalPrefix = None
    
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
            if hasattr(self, '_uploaderName'):
                return self._uploaderName
            else:
                return None
        def fset(self, name):
            
            if not name in availableFormats:
                del(self._uploaderImp)
                error = InputError("Invalid Value")
                raise error
            self._outputFormat = name
            new_implementation_ptr = { 'SMIME' : ,output_driver_smime
                'message' : ,output_driver_message
                'lines' : ,output_driver_lines
                'json' :  output_driver_json,
            }
            new_implementation = new_implementation_ptr[name]()
            new_implementation.fpOutput = self.fpOutput
            new_implementation.saSession = self.saSession
            new_implementation.x509anchor = self.x509anchor
            self._uploaderImp = new_implementation
            
        def fdel(self):
            del self._uploader
    
    
    def subscriptions_lister(self):
        if not hasattr(self, '_uploaderImp'):
            error = InputError("Property 'format' has invalid value.")
            raise error
        return self._uploaderImp.subscriptions_lister()
