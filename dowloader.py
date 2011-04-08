import urllib2
import urllib

def https_read_x509(url,key_file='/etc/grid-security/hostkey.pem',cert_file='/etc/grid-security/hostcert.pem'):
    opener =urllib.URLopener(key_file=key_file,cert_file=cert_file)
    xml = opener.open(url)
    return xml.read()

def https_read_insecure(url):
    url = "https://particle.phys.uvic.ca/~igable/hepix/hepix_signed_image_list"    
    req = urllib2.Request(url=url)
    f = urllib2.urlopen(req)
    return f.read()

def https_read(url):
    # We use insecure system for now
    # man in middle can block upgrades
    return https_read_insecure(url)


def main():
    url = "https://particle.phys.uvic.ca/~igable/hepix/hepix_signed_image_list"    
    message = https_read(url)

if __name__ == "__main__":
    main()
