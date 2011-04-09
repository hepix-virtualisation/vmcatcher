import databaseDefinition as model
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine



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

class Database():
    def __init__(self,engine):
        self.engine = engine
        self.SessionFactory = sessionmaker(bind=self.engine)
    def ImageListSubscribe(self,message):
        session = self.SessionFactory()
        dq = DatabaseQuerys(session)
        endorser = dq.getendorser('/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
        if not endorser:
            # No endorser we must create.
            endorser = dq.create_endorser('/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable')
            print "None? %s" % (endorser)
            for item in session.query(model.Endorser):
                print "item.hv_dn = %s" % (item.hv_dn)
                

engine = create_engine('sqlite:///tutorial.db', echo=False)
model.init(engine)
#Endorser_Add()
db = Database(engine)
db.ImageListSubscribe('s')

