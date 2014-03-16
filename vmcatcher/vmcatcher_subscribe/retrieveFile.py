import retrieveBase
import logging




class retrieve(retrieveBase.retrieve):
    def __init__(self, *args, **kwargs):
        retrieveBase.retrieve.__init__(self,args,kwargs)
    def requestAsString(self):
        output = {}
        content = None
        if not os.path.exists(path):
            output['error'] = 'file noes not exist'
            output['code'] = 1
            return output
        with open(self.path, 'r') as content_file:
            content = content_file.read()
        output['responce'] = content
        output['code'] = 0
        return output
 
