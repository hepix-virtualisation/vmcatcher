from sqlalchemy import create_engine
import hepixvmlis.databaseDefinition as model
import hepixvmlis.databaseView as databaseView

import logging
import optparse
import smimeX509validation.loadcanamespace as loadcanamespace
import sys
from hepixvmlis.__version__ import version

from sqlalchemy.orm import sessionmaker
import hepixvmlis
import urllib2
import urllib
import json

from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder

def formatter(filename):
    print filename
    pass
class db_actions(hepixvmlis.databaseView.DatabaseQuerys):

    def __init__(self,session):
        self.session = session
        
    def subscribe_file(self,filename):
        req = urllib2.Request(url=filename)
        f = urllib2.urlopen(req)
        jsontext = json.load(f)
        vmilist = VMimageListDecoder(jsontext)
        
        metadata = {}
        metadata.update(vmilist.metadata)
        metadata.update(vmilist.endorser.metadata)
        self.subscription_create(metadata,authorised=True)

    def subscriptions_lister(self,formatter2 = formatter):
        output = ''

        subauthq = self.session.query(model.SubscriptionAuth).all()


        #print self.session.query(model.SubscriptionAuth).count()
        subauthq = self.session.query(model.Subscription).all()
        for item in subauthq:
            obj = {u'dc:identifier' : str(item.uuid),
                    u'dc:description' : str(item.description),
                    u'hv:uri' : str(item.url),
                    u'authorised' : str(item.authorised),
                    }
            output += json.dumps(obj, sort_keys=True, indent=4)
        return output




def main():
    """Runs program and handles command line options"""
    actions = set([])
    dbinitiation_default = 'sqlite:///tutorial.db'
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-l', '--list', action ='store_true',help='list subscriptions', metavar='OUTPUTFILE')
    p.add_option('-d', '--database', action ='store', help='Database Initiation string',
        default='sqlite:///tutorial.db')
    p.add_option('-s', '--subscribe', action ='append',help='Subscribe', metavar='INPUTFILE')
    options, arguments = p.parse_args()
    anchor =  loadcanamespace.ViewTrustAnchor()

    subscription_url_list = []
    if options.list:
        actions.add('list')
    if options.subscribe:
        
        actions.add('subscribe')
        for subscriptions_ui in options.subscribe:
            subscription_url_list.append(subscriptions_ui)
        
    if len(actions) == 0:
        return
    # 1 So we have some actions to process
    
    # 1.1 Initate DB
    engine = create_engine(options.database, echo=False)
    model.init(engine)
    SessionFactory = sessionmaker(bind=engine)

    if 'subscribe' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        for uri in subscription_url_list:
            db.subscribe_file(uri)
            
    if 'list' in actions:
        Session = SessionFactory()
        db = db_actions(Session)
        print db.subscriptions_lister()
       
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
