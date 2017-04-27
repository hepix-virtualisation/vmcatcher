import logging
from vmcatcher.outputbase import output_driver_base
from vmcatcher.outputbase import output_driver_lister
from vmcatcher.outputbase import output_driver_display_metadata

class output_driver_lines(output_driver_display_metadata, output_driver_lister,output_driver_base):
    def __init__(self):
        output_driver_base.__init__(self)
        output_driver_lister.__init__(self)
        output_driver_display_metadata.__init__(self)
        self.log = logging.getLogger("output_driver_lines")
