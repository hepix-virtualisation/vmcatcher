import urlparse

def uriNormalise(value):
    output = setUri( value)
    return getUri(output)

def uriNormaliseAnonymous(value):
    output = setUri( value)
    return getUriAnonymous(output)

def setUri(value):
    target = {}
    if isinstance(value,  str):
        value = unicode(value)
    if not isinstance(value,  unicode):
        value = u""
    parsed = urlparse.urlparse(value)
    target["protocol"] = parsed.scheme
    newServer = None
    newPort = None
    newUsername = None
    newPassword = None
    if len(parsed.netloc) > 0:
        netloc = parsed.netloc.split('@')
        hostPort = ""
        userPass = ""
        if len(netloc) == 1:
            hostPort = netloc[0]
        if len(netloc) == 2:
            userPass = netloc[0]
            hostPort = netloc[1]
        if len(userPass) > 0:
            splitUserPass = userPass.split(':')
            newUsername = splitUserPass[0]
            if len(splitUserPass) > 1:
                newPassword = ':'.join([str(x) for x in splitUserPass[1:]])
        if len(hostPort) > 0:
            splitHostPort = hostPort.split(':')
            newServer = splitHostPort[0]
            if len(splitHostPort) == 2:
                asInt = int(splitHostPort[1])
                if asInt != 0:
                    newPort = asInt
    target["server"] = newServer
    target["port"] = newPort
    target["username"] = newUsername
    target["password"] = newPassword
    if len(parsed.path) > 0:
        target["path"] = parsed.path
    else:
        target["path"] = None
    return target



def getUri(target):
    if target["protocol"] == None:
        return None
    userPass = u""
    if target["username"] != None:
        userPass = target["username"]
        if target["password"] == None:
            userPass = target["username"]
        else:
            userPass = u"%s:%s" % (target["username"], target["password"])
    hostPort = ""
    if target["server"] != None:
        if target["port"] == None:
            hostPort = target["server"]
        else:
            hostPort = u"%s:%s" % (target["server"], target["port"])
    netloc = ""
    if (len(hostPort) > 0):
        if (len(userPass) > 0):
            netloc = u"%s@%s" % (userPass, hostPort)
        else:
            netloc = hostPort
    path = ""
    if target["path"] != None:
        path = target["path"]
    output = u"%s://%s%s" % (target["protocol"],netloc,path)
    return output
    
def getUriAnonymous(target):
    if target["protocol"] == None:
        return None
    userPass = ""
    hostPort = ""
    if target["server"] != None:
        if target["port"] == None:
            hostPort = target["server"]
        else:
            hostPort = "%s:%s" % (target["server"], target["port"])
    netloc = ""
    if (len(hostPort) > 0):
        if (len(userPass) > 0):
            netloc = "%s@%s" % (userPass, hostPort)
        else:
            netloc = hostPort
    path = ""
    if target["path"] != None:
        path = target["path"]
    output = "%s://%s%s" % (target["protocol"],netloc,path)
    return output
