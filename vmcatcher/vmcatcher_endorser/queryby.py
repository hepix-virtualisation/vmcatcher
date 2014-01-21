import logging

import vmcatcher.databaseDefinition as model

class queryby_base:
    """"Base class for querying subscriptions"""
    def __init__(self,session):
        self.session = session
    def subscription_by_id(self,private_id):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.id==private_id)
        return subscriptionlist
    def subscription_by_uri(self,url):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.url==url)
        return subscriptionlist
    def subscription_by_uuid(self,uuid):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.uuid==uuid)
        return subscriptionlist
    def imagelist_by_id(self,private_id):
        subscriptionlist = self.session.query(model.Imagelist).\
                filter(model.Imagelist.id==private_id)
        return subscriptionlist

        # Now the virtual class
    def subscription_get(self,by_id):
        return self.subscription_by_id(private_id)
    def endorser_all(self):
        return self.session.query(model.Endorser).all()
    def endorser_by_uuid(self,uuid):
        endorser_list = self.session.query(model.Endorser).\
                filter(model.Endorser.identifier==uuid)
        return endorser_list
    def princible_by_endorserId(self,identifier):
        princible_list = self.session.query(model.EndorserPrincible).\
                filter(model.EndorserPrincible.endorser == identifier)
        return princible_list
    def subscriptionAuth_by_endorserId(self,identifier):
        subauth_list = self.session.query(model.SubscriptionAuth).\
                filter(model.SubscriptionAuth.endorser == identifier)
        return subauth_list
    def links_all(self):
        return self.session.query(model.Subscription,model.Endorser,model.SubscriptionAuth).\
            filter(model.Endorser.id==model.SubscriptionAuth.endorser).\
            filter(model.Subscription.id==model.SubscriptionAuth.subscription)
            
class queryby_uri(queryby_base):
    def subscription_get(self,url):
        return self.subscription_by_uri(url)

class queryby_uuid(queryby_base):
    def subscription_get(self,uuid):
        return self.subscription_by_uuid(uuid)

