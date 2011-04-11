from sqlalchemy import create_engine

import hepixvmlis.databaseView as databaseView

import logging
import optparse
import smimeX509validation.loadcanamespace as loadcanamespace
import sys
from hepixvmlis.__version__ import version


def main():
    """Runs program and handles command line options"""
    actions = set([])
    p = optparse.OptionParser(version = "%prog " + version)
    p.add_option('-l', '--list', action ='store_true',help='list subscriptions', metavar='OUTPUTFILE')
    p.add_option('-d', '--database', action ='store', help='Path of the json output file', metavar='OUTPUTFILE')
    
    options, arguments = p.parse_args()
    anchor =  loadcanamespace.ViewTrustAnchor()
    if options.list:
        format = options.format
        actions.add('list')
    print actions
    
       
if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
