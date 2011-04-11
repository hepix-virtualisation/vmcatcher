import databaseDefinition as model
from sqlalchemy.orm import sessionmaker
import dowloader as downloader

class DatabaseQuerys():
    def __init__(self,session):
        self.session = session
    def getendorser(self,dn):
        found = None
        qr = self.session.query(model.Endorser).filter(model.Endorser.hv_dn==dn)
        for item in qr:
            found = item
            break
        return found
    def create_endorser(self,dn):
        ed_user = model.Endorser('Ian Gable', '/C=CA/O=Grid/CN=Grid Canada Certificate Authority','/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
        #print ed_user.dc_creator
        try:
            self.session.add(ed_user)
            self.session.commit()
        except  :
            self.session.rollback()
            print "already exists"

            ed_user = None
            for instance in self.session.query(model.Endorser).order_by(model.Endorser.id):
                ed_user = instance
        print "got it %s %s" % (ed_user.dc_creator, ed_user.hv_dn)
        return ed_user
    def Imagelist_Get(self, uuid):
        found = None
        qr = self.session.query(model.Imagelist).filter(model.Imagelist.identifier==uuid)
        for item in qr:
            found = item
            break
        return found
    def Imagelist_Create(self,uuid,endorsedmetadata,url,endorser):
        print "uuid=%s" % (uuid)
        newlist = model.Imagelist( uuid ,endorsedmetadata,url,endorser)
        try:
            self.session.add(newlist)
            self.session.commit()
        except  :
            self.session.rollback()
            print "already exists"
class Database():
    def __init__(self,engine):
        self.engine = engine
        self.SessionFactory = sessionmaker(bind=self.engine)
    def ImageListSubscribe(self,metadata):
        uuid = metadata[u'dc:identifier']
        #endorsed = metadata[]
        url = metadata[u'hv:uri']

        #print message
        session = self.SessionFactory()
        
        document = downloader.https_read(url)
        print document
        
        
        dq = DatabaseQuerys(session)
        endorser = dq.getendorser('/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
        vmilist = dq.Imagelist_Get('63175437-7d59-4851-b333-c96cb6545a86')
        if not vmilist:
            if not endorser:
                endorser = dq.create_endorser('/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
            vmilist = dq.Imagelist_Create(uuid,document,url,endorser)
        
        
            # No endorser we must create.
            
        print "None? %s" % (endorser)
        uuid = "63175437-7d59-4851-b333-c96cb6545a86"
        endorsedmetadata = document
        
      
    def ImageListUpdate(self,updator):
        session = self.SessionFactory()
        quertyresult = session.query(model.Imagelist)
        print "len(quertyresult)='%s'" % (quertyresult.count())

        for item in quertyresult:
            
            updator.update(item)
class Updater():
    def update(self, imagelist):
        #DatabaseQuerysViewTrustAnchor
        print "UUID=%s" % (imagelist.identifier)
        print "imagelist.url=%s" % (imagelist.url)
        print "imagelist.endorsedmetadata,%s" % (imagelist.endorsed)
        print "imagelist.endorser%s" % (imagelist.endorser)

def init(engine):
    model.init(engine)
    
