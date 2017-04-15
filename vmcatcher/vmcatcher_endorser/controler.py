from sqlalchemy import create_engine
import vmcatcher.databaseDefinition as model
import os
import logging
import optparse
from smimeX509validation import TrustStore, LoadDirChainOfTrust,smimeX509validation, smimeX509ValidationError
import sys
from vmcatcher.__version__ import version

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, DatabaseError, ProgrammingError
import vmcatcher
import urllib2
import urllib
import hashlib
import datetime
from hepixvmitrust.vmitrustlib import VMimageListDecoder as VMimageListDecoder
from hepixvmitrust.vmitrustlib import time_format_definition as time_format_definition
try:
    import json
except:
    import simplejson
from vmcatcher.listutils import pairsNnot
import vmcatcher.outputfacard

# User interface

import vmcatcher.queryby

class db_controler:
    def __init__(self,dboptions,dblog = False):
        self.log = logging.getLogger("db_controler")
        self.engine = create_engine(dboptions, echo=dblog)
        model.init(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.anchor = None
        self.factory_selector = None
        self.selectors_available = ["endorser_uuid"]
        self.selector_curent = None
        self._outputter = vmcatcher.outputfacard.outputFacade()
    def set_selector(self,selector_string):
        self.selector_curent = None
        if not selector_string in self.selectors_available:
            self.log.warning("Invalid selector string set:%s" % (selector_string))
            return False
        if selector_string == 'endorser_uuid':
            self.selector_curent = vmcatcher.queryby.query_endorser_by_identifier
        elif selector_string == 'sub_uri':
            self.selector_curent = vmcatcher.queryby.query_subscriptions_by_uri
        return True
    def setup_trust_anchor(self,directory):
        self.anchor = LoadDirChainOfTrust(directory)

    def setup_view_format(self,format):
        self._outputter.format = format

    def endosers_list(self):
        Session = self.SessionFactory()
        self._outputter.fpOutput = sys.stdout
        self._outputter.saSession = Session
        self._outputter.x509anchor = self.anchor
        self._outputter.list_vmcatcher_endorser_cred()
        return True
    def links_list(self):
        Session = self.SessionFactory()
        self._outputter.fpOutput = sys.stdout
        self._outputter.saSession = Session
        self._outputter.x509anchor = self.anchor
        self._outputter.list_vmcatcher_endorser_link()
        return True
    def link(self,endorsers_selected,subscriptions_selected):
        pairs, extra_selectors ,extra_paths = pairsNnot(endorsers_selected,subscriptions_selected)
        Session = self.SessionFactory()
        for pair in pairs:
            endorser = pair[0]
            subscription = pair[1]
            subauth_list = Session.query(model.Endorser,model.Subscription,model.SubscriptionAuth).\
                filter(model.Endorser.identifier == endorser).\
                filter(model.Subscription.identifier == subscription).\
                filter(model.SubscriptionAuth.endorser == model.Endorser.id).\
                filter(model.SubscriptionAuth.subscription == model.Subscription.id)
            if subauth_list.count() == 0:
                endorser_list = Session.query(model.Endorser).\
                    filter(model.Endorser.identifier == endorser)
                if endorser_list.count() == 0:
                    self.log.warning("endorser not available.")
                    continue
                sub_list = Session.query(model.Subscription).\
                    filter(model.Subscription.identifier == subscription)
                if sub_list.count() == 0:
                    self.log.warning("subscription not available.")
                    continue
                db_endorser = endorser_list.one()
                db_sub = sub_list.one()
                newsubauth = model.SubscriptionAuth(db_sub.id,db_endorser.id,True)
                Session.add(newsubauth)
                Session.commit()
            else:
                self.log.warning("endorser and subscription already linked.")


    def unlink(self,endorsers_selected,subscriptions_selected):
        Session = self.SessionFactory()
        pairs, extra_selectors ,extra_paths = pairsNnot(endorsers_selected,subscriptions_selected)
        for pair in pairs:
            endorser = pair[0]
            subscription = pair[1]
            subauth_list = Session.query(model.Endorser,model.Subscription,model.SubscriptionAuth).\
                filter(model.Endorser.identifier == endorser).\
                filter(model.Subscription.identifier == subscription).\
                filter(model.SubscriptionAuth.endorser == model.Endorser.id).\
                filter(model.SubscriptionAuth.subscription == model.Subscription.id)
            if subauth_list.count() == 0:
                self.log.warning("endorser and subscription are not linked.")
            else:
                for query_row in subauth_list:
                    db_endorser = query_row[0]
                    db_sub = query_row[1]
                    db_subAuthEnd = query_row[2]
                    Session.delete(db_subAuthEnd)
                    Session.commit()

    def endorsers_info(self,selected):
        errorhappened = False
        Session = self.SessionFactory()
        for selector_filter in selected:
            output_fileptr = sys.stdout
            query_endorser = self.selector_curent(Session,selector_filter)
            if query_endorser.count() == 0:
                self.log.error("endorser '%s' not found" % (selector_filter))
                continue
            self._outputter.fpOutput = sys.stdout
            self._outputter.saSession = Session
            self._outputter.x509anchor = self.anchor
            for endorser in query_endorser:
                self._outputter.display_endorser(endorser)
                princible_query = Session.query(model.EndorserPrincible).\
                    filter(model.EndorserPrincible.endorser == endorser.id)

                if princible_query.count() == 0:
                    self.log.warning("endorser '%s' has no princibles" % (selector_filter))
                else:
                    pass
        return True

    def endorser_create(self,endorser,subjects,issuers):
        # Check input parameters.
        pairs, extra_subs ,extra_issuers = pairsNnot(subjects,issuers)
        if len(extra_subs) > 0:
            if len(issuers) > 1:
                self.log.warning("Unsure how to add subjects credentials without issuer credentials.")
                return False
            else:
                if len (issuers) > 0:
                    thisissuer = issuers[0]
                    for this_sub in extra_subs:
                        pairs.append([this_sub,thisissuer])
                else:
                    self.log.warning("Cant add subjects credentials without issuer credentials.")
                    return False
        if len (extra_issuers) > 0:
            self.log.warning("Cant add issuer credentials, without a subject.")
            return False
        if len(pairs) == 0:
            return True
        # Now we process requests
        error = False
        deleteOnError = False
        Session = self.SessionFactory()
        endorserQuery = Session.query(model.Endorser).\
                filter(model.Endorser.identifier==endorser)
        endorserObj = None
        if endorserQuery.count() == 0:
            endorserObj = model.Endorser({'dc:identifier' : str(endorser)})
            Session.add(endorserObj)
            Session.commit()
            deleteOnError = True
            endorserQuery = Session.query(model.Endorser).\
                filter(model.Endorser.identifier==endorser)

        endorserObj = endorserQuery.one()
        endorserObjId = int(endorserObj.id)
        for pair in pairs:
            dn = pair[0]
            issuer = pair[1]
            cred = model.EndorserPrincible(endorserObjId,{u'hv:dn' : dn, u'hv:ca' : issuer})
            Session.add(cred)
            try:
                Session.commit()
            except IntegrityError as expt:
                self.log.error("Database integrity error while adding '%s' credentials to  '%s'." % (dn,endorser))
                self.log.debug(E.params)
                Session.rollback()
                error = True
                break
        if error and deleteOnError:
            endorserQuery = Session.query(model.Endorser).\
                filter(model.Endorser.identifier==endorser)
            if endorserQuery.count() > 0:
                EndorserToDel = endorserQuery.one()
                Session.delete(EndorserToDel)
                Session.commit()
                return False
        return True
    def endorser_delete(self,endorsers):
        # Check input parameters.
        Session = self.SessionFactory()
        for endorser in endorsers:
            endorserQuery = Session.query(model.Endorser).\
                filter(model.Endorser.identifier==endorser)
            if endorserQuery.count() == 0:
                self.log.warning("Failed to find endorser '%s'." % (endorser))
                continue
            for obj in endorserQuery:
                Session.delete(obj)
                self.log.info("Deleting endorser '%s'." % (endorser))
            Session.commit()




