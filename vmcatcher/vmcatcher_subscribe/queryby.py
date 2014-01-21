import vmcatcher.databaseDefinition as model

class queryby_base(object):
    """"Base class for querying subscriptions"""
    def __init__(self,session):
        self.session = session
    def subscription_by_id(self,private_id):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.id==private_id)
        return subscriptionlist
    def subscription_by_uri(self,uri):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.uri==uri)
        return subscriptionlist
    def subscription_by_uuid(self,uuid):
        subscriptionlist = self.session.query(model.Subscription).\
                filter(model.Subscription.identifier==uuid)
        return subscriptionlist
    def imagelist_by_id(self,private_id):
        subscriptionlist = self.session.query(model.ImageListInstance).\
                filter(model.ImageListInstance.id==private_id)
        return subscriptionlist

        # Now the virtual class
    def subscription_get(self,by_id):
        return self.subscription_by_id(private_id)


class queryby_uri(queryby_base):
    def subscription_get(self,url):
        return self.subscription_by_uri(url)

class queryby_uuid(queryby_base):
    def subscription_get(self,uuid):
        return self.subscription_by_uuid(uuid)

