import retrieveBase
import logging
import os.path



class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
    def requestAsString(self):
        if self.path == None:
            output['error'] = 'Path not defined'
            output['code'] = 404
            return output
        output = {}
        content = None
        if not os.path.exists(self.path):
            output['error'] = 'file noes not exist'
            output['code'] = 10
            return output
        with open(self.path, 'r') as content_file:
            content = content_file.read()
        output['responce'] = content
        output['code'] = 0
        return output
 
