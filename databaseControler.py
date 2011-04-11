from sqlalchemy import create_engine

import databaseView

import logging
import optparse
import smimeX509validation.loadcanamespace as loadcanamespace
import sys


def main():
    p = optparse.OptionParser()
    p.add_option('-m', '--message', action ='append', 
        help='adds a message to be tested.')
    p.add_option('-i', '--import', action ='append', 
        help='adds a url subscription.')
    p.add_option('-u', '--update', action ='store', 
        help='Path of certificates dir',
        default='/etc/grid-security/certificates/')
    options, arguments = p.parse_args()
    anchor =  loadcanamespace.ViewTrustAnchor()
    
    if options.message == None:
        sys.exit(1)
    else:
        for item in options.message:
            output = anchor.validate_file(item)
            print output
       
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    engine = create_engine('sqlite:///tutorial.db', echo=False)
    
    databaseView.init(engine)
    #Endorser_Add()
    db = databaseView.Database(engine)
    subbuilder = {u'dc:date:created':"2011-03-16T00:15:07Z",
        u'dc:date:expires':"2011-04-13T00:15:07Z",
        u'dc:identifier':"63175437-7d59-4851-b333-c96cb6545a86",
        u'dc:description':"HEPiX Image Exchange Testing",
        u'dc:title':"HEPiX-Image-Exchange",
        u'dc:source':"https://particle.phys.uvic.ca/~igable/hepix/hepix_signed_image_list",
        u'hv:version':5,
        u'hv:uri':"https://particle.phys.uvic.ca/~igable/hepix/hepix_signed_image_list",
        u'hv:dn':'/C=CA/O=Grid/OU=phys.uvic.ca/CN=Ian Gable',
        u"hv:ca": "/C=CA/O=Grid/CN=Grid Canada Certificate Authority",
    }
    subscription = db.ImageListSubscribe(subbuilder)

    # This is done so the process can be threaded
    updater = databaseView.Updater()
    db.ImageListUpdate(updater)
    main()
