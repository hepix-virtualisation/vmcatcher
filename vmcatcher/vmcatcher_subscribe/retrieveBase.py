import logging



def Property(func):
    return property(**func())

class retrieve(object):
    def __init__(self, *args, **kwargs):
        self.port_default = None


    @Property
    def port():
        doc = "port to retrieve from"
        def fget(self):
            return self._port
        def fset(self, value):
            if value == None:
                value = self.port_default
            self._port = value
        def fdel(self):
            del self._port
        return locals()


    @Property
    def trustanchor_needed():
        doc = "port to retrieve from"
        def fget(self):
            return False
        def fset(self, value):
            pass
        def fdel(self):
            pass
        return locals()
