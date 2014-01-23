import vmcatcher.databaseDefinition as model

def query_subscriptions_by_identifier(session, identifier):
    return session.query(model.Subscription).\
                filter(model.Subscription.identifier == identifier)

def query_subscriptions_by_uri(session, uri):
    return session.query(model.Subscription).\
                filter(model.Subscription.uri == uri)
    
def query_imageDef_by_identifier(session, identifier):
    return session.query(model.ImageDefinition).\
                filter(model.ImageDefinition.identifier == identifier)
    
def query_imageDef_by_sha512(session, sha512):
    return session.query(model.ImageDefinition).\
                filter(model.ImageListInstance.id==model.ImageInstance.fkimagelistinstance).\
                filter(model.ImageInstance.sha512 == sha512).\
                filter(model.ImageInstance.fkIdentifier == model.ImageDefinition.id)

def query_endorser_by_identifier(session, identifier):
    return session.query(model.Endorser).\
                filter(model.Endorser.identifier == identifier)
