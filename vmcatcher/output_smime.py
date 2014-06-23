import logging
from vmcatcher.outputbase import output_driver_base
from vmcatcher.outputbase import output_driver_lister
from vmcatcher.outputbase import output_driver_lister
from vmcatcher.outputbase import output_driver_display_metadata
from vmcatcher.outputbase import output_driver_display_message
class output_driver_smime(output_driver_display_message,output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        output_driver_display_message.__init__(self)
        self.log = logging.getLogger("output_driver_smime")

    def info(self, *args, **kwargs):
        expectedkeys = set([
                "Endorser",
                "EndorserPrincible",
                "ImageDefinition",
                "ImageInstance",
                "ImageListInstance",
                "Subscription",
                "SubscriptionAuth",
                ])
        
        found = set(kwargs.keys())
        if "ImageListInstance" in found:
            argImageInstance = kwargs.get('ImageListInstance', None)
            self.fpOutput.write (argImageInstance.data)
            return True
        return False
