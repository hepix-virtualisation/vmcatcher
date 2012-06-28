vmlisub

[Prev](imagetransfer-software-subscriber.shtml) 

Chapter 10. `Virtual Machine Image List`{.literal} Subscribing Software

 [Next](imagetransfer-software-site.shtml)

* * * * *

[HEPIX Virtualisation Working Group](../index.shtml) \>
[`Virtual Machine Image`{.literal} Transfer](imagetransfer.shtml) \>
[`Virtual Machine Image List`{.literal} Subscribing
Software](imagetransfer-software-subscriber.shtml) \> vmlisub

vmlisub
-------

This virtual maschine `Virtual Machine Image List`{.literal} subscriber
implementation is intended to be a production grade referance
implementation.

[[return to top](imagetransfer-software-vmlisub.shtml)]

### Introduction

This application allows users to subscribe to virtual machine
`Virtual Machine Image List`{.literal}s, cache the images referenced to
in the `Virtual Machine Image List`{.literal}, validate the images list
with x509 based public key cryptography, and validate the images against
sha512 hashes in the images lists and provide events for further
applications to process updates or expiries of virtual machine images
without having to further validate the images.

This software is available at:

`https://github.com/hepix-virtualisation/hepixvmilsubscriber`{.code}

The software is based upon a simple database that stores subscriptions
to `Virtual Machine Image List`{.literal}s, who can sign the
`Virtual Machine Image List`{.literal}, and which images belong to which
subscriptions. It allows images to selected for subscription.

Subscribed images can be downloaded verified and cached. Cached images
can be verified, and if invalid or expired they are moved to an expiry
directory.

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Features

-   Add and delete multiple subscriptions to
    `Virtual Machine Image List`{.literal}s.
-   Update subscriptions checking authenticity of the message useng x509
    based signatures.
-   Automation as a cron script.
-   Subscribe and unsubscribe to images from
    `Virtual Machine Image List`{.literal}s.
-   Download verify images into a local cache.
-   Expire images to an archive when no longer endorsed or corrupt.

This set of applications are designed to provide a similar work flow
from each area of control to the `Virtual Machine Image List`{.literal}
archive.

-   vmlisub\_endorser - Endorsers of
    `Virtual Machine Image List`{.literal} subscriptions.
-   vmlisub\_sub - Subscription list details.
-   vmlisub\_image - Image details.
-   vmlisub\_cache - Cache images and update events.

They work in conjunction with a database to ease navigation, a local
cache of `Virtual Machine Image List`{.literal} subscriptions. The
database is message format agnostic, but it authenticates and validates
all messages in import. Because these are just caches of
`Virtual Machine Image List`{.literal}s they are meant to be used the
majority of the time without intervention.

If you are signing a list using the hepix
`Virtual Machine Image List`{.literal} signer, you should also install
this application and subscribe to your current image.

It is intended to with a couple of cron scripts to be informed at any
time if your local images are matching signatures in the
`Virtual Machine Image List`{.literal}.

Anyone curious about this application should consider this application a
software application similar to Debian’s ’aptitude’ or Redhats ’yum’,
but rather for virtual machines, authenticated by the x509 signatures.

[[return to top](imagetransfer-software-vmlisub.shtml)]

### Quick start use of hepixvmilsubscriber

First make sure that all the Certificate Revocation Lists (CRL) are upto
date.

~~~~ {.programlisting}
[root] #  fetch-crl
~~~~

To add a subscription,

~~~~ {.programlisting}
[user] $  wget --no-check-certificate https://cernvm.cern.ch/releases/image.list
~~~~

Now you can check the `Virtual Machine Image List`{.literal} by visiual
inspection.

~~~~ {.programlisting}
[user] $  grep 'hv:[cd][an]' hepix_signed_image_list
                "hv:ca": "/DC=ch/DC=cern/CN=CERN Trusted Certification Authority", 
                "hv:dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic", 
~~~~

Now create this endorser. The endorser\_uuid can be any string but its
recommended this is a short string possibly following the uuid standard:

~~~~ {.programlisting}
[user] $  vmlisub_endorser --create \
       --endorser_uuid='Ian' \
       --subject='/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic' \
       --issuer='/DC=ch/DC=cern/CN=CERN Trusted Certification Authority'
~~~~

Now we can add the subscription, this will automatically link the
endorser with this subscription.

~~~~ {.programlisting}
[user] $  vmlisub_endorser -l
Ian    '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic'        '/DC=ch/DC=cern/CN=CERN Trusted Certification Authority'
~~~~

The above command will show you the endorsers. Note the first column is
the identifier. In this case its shorter than a UUID. The second column
is the users certificate subject (some times know as distinguished name)
while the third column is the subject of the issuing certificate
authority.

~~~~ {.programlisting}
[user] $  vmlisub_sub -s file:////`pwd`/hepix_signed_image_list
INFO:main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
WARNING:db_actions:list hv:uri does not match subscription uri
~~~~

Although less secure it is also possible to add the option
’--auto-endorse’ to the command line so that the users, and issuer’s
certificates are auto added to the database when subscribing.

~~~~ {.programlisting}
[user] $  vmlisub_sub  --auto-endorse -s file:////`pwd`/hepix_signed_image_list
INFO:main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
WARNING:db_actions:list hv:uri does not match subscription uri
~~~~

List the registered Images.

~~~~ {.programlisting}
[user] $  vmlisub_image -l
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
327016b0-6508-41d2-bce0-c1724cb3d3e2    0       63175437-7d59-4851-b333-c96cb6545a86
858a817e-0ca2-473f-89d3-d5bdfc51968e    0       63175437-7d59-4851-b333-c96cb6545a86
da42ca85-179b-4873-b12e-32d549bf02b6    0       63175437-7d59-4851-b333-c96cb6545a86
~~~~

The results show the UUID of the image, the availability state and the
subscription UUID. The state value is a bitmap, 1 is subscribed, 2 means
its available in the current `Virtual Machine Image List`{.literal}s.
Now we will select an image for local caching.

Next update the subscriptions.

~~~~ {.programlisting}
[user] $  vmlisub_sub -U
INFO:main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
INFO:db_actions:Updating:63175437-7d59-4851-b333-c96cb6545a86
~~~~

Now the data base contains the latest version of the
`Virtual Machine Image List`{.literal}. To query the available images
they can be cached:

~~~~ {.programlisting}
[user] $  vmlisub_image -l
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
327016b0-6508-41d2-bce0-c1724cb3d3e2    2       63175437-7d59-4851-b333-c96cb6545a86
858a817e-0ca2-473f-89d3-d5bdfc51968e    2       63175437-7d59-4851-b333-c96cb6545a86
da42ca85-179b-4873-b12e-32d549bf02b6    2       63175437-7d59-4851-b333-c96cb6545a86
~~~~

Thsi now shows the images are available in the latest
`Virtual Machine Image List`{.literal}.

~~~~ {.programlisting}
[user] $  vmlisub_image -a -u 858a817e-0ca2-473f-89d3-d5bdfc51968e
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
~~~~

The `Virtual Machine Image List`{.literal} state is now changed to

~~~~ {.programlisting}
[user] $  vmlisub_image -l
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
327016b0-6508-41d2-bce0-c1724cb3d3e2    2       63175437-7d59-4851-b333-c96cb6545a86
858a817e-0ca2-473f-89d3-d5bdfc51968e    3       63175437-7d59-4851-b333-c96cb6545a86
da42ca85-179b-4873-b12e-32d549bf02b6    2       63175437-7d59-4851-b333-c96cb6545a86
~~~~

Clearly showing that the image ’858a817e-0ca2-473f-89d3-d5bdfc51968e’ is
subscribed.

Make the directories for caching the images.

~~~~ {.programlisting}
[user] $  mkdir cache cache/partial cache/expired
~~~~

Now cache the images.

~~~~ {.programlisting}
[user] $  vmlisub_cache
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
INFO:DownloadDir:Downloading '858a817e-0ca2-473f-89d3-d5bdfc51968e'.
INFO:CacheMan:moved file 858a817e-0ca2-473f-89d3-d5bdfc51968e
~~~~

Once this is complete the image from the
`Virtual Machine Image List`{.literal} will be cached.

~~~~ {.programlisting}
[user] $  find cache/
cache/
cache/partial
cache/partial/cache.index
cache/expired
cache/expired/cache.index
cache/858a817e-0ca2-473f-89d3-d5bdfc51968e
cache/cache.index
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Set up for Production using Cron

Then the by hand configuration for your master DB

~~~~ {.programlisting}
[root] #  useradd vmlisub
~~~~

~~~~ {.programlisting}
[root] #  mkdir -p /var/lib/vmlisub /var/cache/vmimages/endorsed \
      /var/cache/vmimages/partial /var/cache/vmimages/expired
~~~~

~~~~ {.programlisting}
[root] #  touch /var/log/vmlisub.log
~~~~

~~~~ {.programlisting}
[root] #  chown vmlisub:vmlisub /var/lib/vmlisub  /var/cache/vmimages/endorsed \
      /var/cache/vmimages/partial /var/cache/vmimages/expired \
      /var/log/vmlisub.log
~~~~

~~~~ {.programlisting}
[root] #  sudo -u vmlisub /usr/bin/vmlisub_sub \
      -s https://cernvm.cern.ch/releases/image.list \
      -d sqlite:////var/lib/vmlisub/vmlisub.db
~~~~

make a cron job

~~~~ {.programlisting}
[root] #  cat   /etc/cron.d/vmlisub
50 */6 * * *    vmlisub (/usr/bin/vmlisub_sub -d sqlite:////var/lib/vmlisub/vmlisub.db -U; /usr/bin/vmlisub_cache -d sqlite:////var/lib/vmlisub/vmlisub.db -C /var/cache/vmimages/endorsed/ -p /var/cache/vmimages/partial/ -e /var/cache/vmimages/expired/ ) >> /var/log/vmlisub.log 2>&1
~~~~

So the script is executed every 6 hours shortly after fetch CRL.

Now at any time users with file permisions can get a list of valid
images.

~~~~ {.programlisting}
[user] $  vmlisub_image -l -d sqlite:////var/lib/vmlisub/vmlisub.db
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

### Installation

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Package Repositories.

The intra site tools are tested on every release for Redhat Enterprise
Linux 5 and 6 and are developed on the Debian Linux platform. They are
available as src and binary RPM packages in the following repository
sporting.

-   http://grid.desy.de/vm/repo/yum/sl6/noarch/RPMS.stable/
-   http://grid.desy.de/vm/repo/yum/sl5/noarch/RPMS.stable/

Deployment instructions are provided in the README included in the
source code and the RPM.

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Installation on Redhat Enterprise Linux 6

Install EPEL for dependencies.

~~~~ {.programlisting}
[root] # rpm -i http://download.fedora.redhat.com/pub/epel/6/x86_64/epel-release-6-5.noarch.rpm
~~~~

Install DESY yum repository.

~~~~ {.programlisting}
[root] # cat /etc/yum.repos.d/desyvirt.repo
[desyvirt]
name=desyvirt
baseurl=http://grid.desy.de/vm/repo/yum/sl6/noarch/RPMS.stable/
enabled=1
gpgcheck=0
~~~~

Install the Grid CA repository for details please see
https://wiki.egi.eu/wiki/EGI\_IGTF\_Release

~~~~ {.programlisting}
[root] # cat /etc/yum.repos.d/egi-trust-anchor.repo
[EGI-trustanchors]
name=EGI-trustanchors
baseurl=http://repository.egi.eu/sw/production/cas/1/current/
gpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3
gpgcheck=1
enabled=1
~~~~

install the ca-policy-egi-core

~~~~ {.programlisting}
[root] # yum install ca-policy-egi-core
~~~~

install fetch-crl

~~~~ {.programlisting}
[root] # yum install fetch-crl
~~~~

~~~~ {.programlisting}
[root] # yum install hepixvmilsubscriber
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Installation on Redhat Enterprise Linux 5

Install EPEL for dependencies.

~~~~ {.programlisting}
[root] # rpm -i http://download.fedora.redhat.com/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
~~~~

Install DESY yum repository.

~~~~ {.programlisting}
[root] # cat /etc/yum.repos.d/desyvirt.repo
[desyvirt]
name=desyvirt
baseurl=http://grid.desy.de/vm/repo/yum/sl5/noarch/RPMS.stable/
enabled=1
gpgcheck=0
~~~~

Install the Grid CA repository for details please see
https://wiki.egi.eu/wiki/EGI\_IGTF\_Release

~~~~ {.programlisting}
[root] # cat /etc/yum.repos.d/egi-trust-anchor.repo
[EGI-trustanchors]
name=EGI-trustanchors
baseurl=http://repository.egi.eu/sw/production/cas/1/current/
gpgkey=http://repository.egi.eu/sw/production/cas/1/GPG-KEY-EUGridPMA-RPM-3
gpgcheck=1
enabled=1
~~~~

Install the lcg-CA

~~~~ {.programlisting}
[root] # yum install lcg-CA
~~~~

install fetch-crl

~~~~ {.programlisting}
[root] # yum install fetch-crl
~~~~

Install the hepix `Virtual Machine Image List`{.literal} subscriber.

~~~~ {.programlisting}
[root] # yum install hepixvmilsubscriber
~~~~

This may fail due to a dependency of m2crypto that cannot be satisfied.
This is due to known bugs in m2crypto in the version shipped in RHEL5.
If this is a problem please download the following

~~~~ {.programlisting}
http://ftp.informatik.uni-frankfurt.de/fedora-archive/fedora/linux/releases/8/Everything/source/SRPMS/m2crypto-0.18-2.src.rpm
~~~~

And build a native RPM.

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Installation on Debian Linux Codename Wheezy or later,

Do not install this on debian 6.0 as the included version of
python-m2crypto is not stable.

These instructions are for Debian Linux Codename Wheezy or later.

Unfortunatly at this moment the code is not packaged. but all the
dependacies are available in the debian repository.

For Grid scientific use you can get a trust store easily using the
egi.eu repository.

~~~~ {.programlisting}
[root] # wget -q -O - \
https://dist.eugridpma.info/distribution/igtf/current/GPG-KEY-EUGridPMA-RPM-3 \
 | apt-key add -
~~~~

Add the following line to your sources.list file for APT:

~~~~ {.programlisting}
#### EGI Trust Anchor Distribution ####
deb http://repository.egi.eu/sw/production/cas/1/current egi-igtf core
~~~~

for example:

~~~~ {.programlisting}
[root] # echo '#### EGI Trust Anchor Distribution ####' >> \
    /etc/apt/sources.list
[root] # echo 'deb http://repository.egi.eu/sw/production/cas/1/current egi-igtf core' >> \
    /etc/apt/sources.list
~~~~

Now install the ` Certification Authorities`{.literal} for the grid
(Other ` Certification Authorities`{.literal} can be substituted),
install a tool to download and cache the
`Certificate Revocation Lists`{.literal}

~~~~ {.programlisting}
[root] # aptitude update
[root] # aptitude install ca-policy-egi-core
[root] # aptitude install fetch-crl
[root] # fetch-crl 
~~~~

Now install the code froms git.

~~~~ {.programlisting}
http://grid.desy.de/vm/repo/yum/sl5/noarch/tgz/
~~~~

The leatest version of hepixvmitrust-X.X.XX.tar.gz shoudl be downloaded
extracted and installed.

~~~~ {.programlisting}
[root] # wget http://grid.desy.de/vm/repo/yum/sl5/noarch/tgz/hepixvmitrust-0.0.14.tar.gz
Resolving grid.desy.de (grid.desy.de)... 131.169.180.46
Connecting to grid.desy.de (grid.desy.de)|131.169.180.46|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 19922 (19K) [application/x-tar]
Saving to: `hepixvmitrust-0.0.14.tar.gz'

100%[======================================>] 19,922      --.-K/s   in 0.05s   

2012-05-28 19:45:45 (413 KB/s) - `hepixvmitrust-0.0.14.tar.gz' saved [19922/19922]
[root] # tar -zxf hepixvmitrust-0.0.14.tar.gz 
[root] # cd hepixvmitrust-0.0.14
[root] # python setup install
[root] # echo $?
[root] # cd ..
~~~~

The leatest version ofsmimeX509validation-0.0.7.tar.gz -X.X.XX.tar.gz
shoudl be downloaded extracted and installed.

~~~~ {.programlisting}
[root] # 
[root] # wget http://grid.desy.de/vm/repo/yum/sl5/noarch/tgz/smimeX509validation-0.0.7.tar.gz
Resolving grid.desy.de (grid.desy.de)... 131.169.180.46
Connecting to grid.desy.de (grid.desy.de)|131.169.180.46|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 19922 (19K) [application/x-tar]
Saving to: `smimeX509validation-0.0.7.tar.gz'

100%[======================================>] 19,922      --.-K/s   in 0.05s   

2012-05-28 19:45:45 (413 KB/s) - `smimeX509validation-0.0.7.tar.gz' saved [19922/19922]
[root] # tar -zxf smimeX509validation-0.0.7.tar.gz 
[root] # cd smimeX509validation-0.0.7
[root] # python setup install
[root] # echo $?
[root] # cd ..
~~~~

The leatest version of hepixvmilsubscriber-X.X.XX.tar.gz shoudl be
downloaded extracted and installed.

~~~~ {.programlisting}
[root] # 
[root] # wget http://grid.desy.de/vm/repo/yum/sl5/noarch/tgz/hepixvmilsubscriber-0.1.14.tar.gz
Resolving grid.desy.de (grid.desy.de)... 131.169.180.46
Connecting to grid.desy.de (grid.desy.de)|131.169.180.46|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 19922 (19K) [application/x-tar]
Saving to: `hepixvmilsubscriber-0.1.14.tar.gz'

100%[======================================>] 19,922      --.-K/s   in 0.05s   

2012-05-28 19:45:45 (413 KB/s) - `hepixvmilsubscriber-0.1.14.tar.gz' saved [19922/19922]
[root] # tar -zxf hepixvmilsubscriber-0.1.14.tar.gz 
[root] # cd hepixvmilsubscriber-0.1.14
[root] # python setup install
[root] # echo $?
[root] # cd ..
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### vmlisub\_endorser

This application is for managing who the subscriber trusts to update
image lists. Since individuals are identified with x509 certificates,
Each certificate has an issuing certificate and a unique string called a
’subject’ to identify the certificate. The ’subject’ of a certificate
and the ’subject’ of the issuing certificate combined are called
’credentials’, and will be globally unique.

ndividuals on rare occasions will need more than one certificate, for
this reason they are given a unique identifier under this system and
allowed to have more than one set of credentials.

Adding a individual to the vmli database.

~~~~ {.programlisting}
[user] $  vmlisub_endorser --create \
       --endorser_uuid=e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
       --subject='/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic' \
       --issuer='/DC=ch/DC=cern/CN=CERN Trusted Certification Authority'
~~~~

Deleting and individual from a vmli database.

~~~~ {.programlisting}
[user] $  vmlisub_endorser --delete \
       --endorser_uuid=e55c1afe-0a62-4d31-a8d7-fb8c825f92a2
~~~~

Allowing an individual to update a subscription.

~~~~ {.programlisting}
[user] $  vmlisub_endorser --link \
       --endorser_uuid=e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
       --subscription_uuid=63175437-7d59-4851-b333-c96cb6545a86
~~~~

Removing an individuals right to update a subscription.

~~~~ {.programlisting}
[user] $  vmlisub_endorser --unlink \
       --endorser_uuid=e55c1afe-0a62-4d31-a8d7-fb8c825f92a2 \
       --subscription_uuid=63175437-7d59-4851-b333-c96cb6545a86
~~~~

Each endorser\_uuid must be unique or they will be assumed to be the
same item. The endorser\_uuid could be a more human name:

~~~~ {.programlisting}
[user] $  vmlisub_endorser --create \
       --endorser_uuid='Ian Gable' \
       --subject='/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=buncic/CN=379010/CN=Predrag Buncic' \
       --issuer='/DC=ch/DC=cern/CN=CERN Trusted Certification Authority'
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### vmlisub\_sub

This application manages your subscriptions and thier update:

To add a subscription

~~~~ {.programlisting}
[user] $  vmlisub_sub  -s https://cernvm.cern.ch/releases/image.list
~~~~

Or alternatively you can download a file visually insepect it and
subscribe to the local file.

~~~~ {.programlisting}
[user] $  vmlisub_sub  -s file:////`pwd`/hepix_signed_image_list
~~~~

To update your subscriptions

~~~~ {.programlisting}
[user] $  vmlisub_sub  -U
~~~~

To list subscriptions

~~~~ {.programlisting}
[user] $  vmlisub_sub  -l
63175437-7d59-4851-b333-c96cb6545a86    True    https://cernvm.cern.ch/releases/image.list
~~~~

Getting Information on a subscription:

~~~~ {.programlisting}
[user] $  vmlisub_sub  -i --uuid=63175437-7d59-4851-b333-c96cb6545a86
dc:identifier=63175437-7d59-4851-b333-c96cb6545a86
subscription.dc:description=CERN Virtual Machine
subscription.sl:authorised=True
subscription.hv:uri=https://cernvm.cern.ch/releases/image.list
subscription.dc:date:updated=2011-04-16T19:23:19Z
imagelist.dc:date:imported=2011-04-16T19:23:18Z
imagelist.dc:date:created=2011-03-16T00:15:07Z
imagelist.dc:date:expires=2011-04-13T00:15:07Z
~~~~

you can also select on the basis of url:

~~~~ {.programlisting}
[user] $  vmlisub_sub  -i -r https://cernvm.cern.ch/releases/image.list
dc:identifier=63175437-7d59-4851-b333-c96cb6545a86
subscription.dc:description=CERN Virtual Machine
subscription.sl:authorised=True
subscription.hv:uri=https://cernvm.cern.ch/releases/image.list
subscription.dc:date:updated=2011-04-17T19:04:35Z
imagelist.dc:date:imported=2011-04-17T19:04:34Z
imagelist.dc:date:created=2011-03-16T00:15:07Z
imagelist.dc:date:expires=2011-04-13T00:15:07Z
~~~~

Change the output format to get the original message without the
security wraper, or in original form:

~~~~ {.programlisting}
[user] $  vmlisub_sub  -i --uuid=63175437-7d59-4851-b333-c96cb6545a86 -f message
~~~~

Three formats exist SMIME, message, lines.

-   SMIME for applications that wish to process the signature as if from
    the endorser directly.
-   message for applications that have no interest in processing the
    SMIME signature.
-   lines for human users of this application.

To delete a subscription

~~~~ {.programlisting}
[user] $  vmlisub_sub  -D  --uuid=63175437-7d59-4851-b333-c96cb6545a86
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### vmlisub\_image

This application manages images within your subscription.

List the available images

~~~~ {.programlisting}
[user] $  vmlisub_image -l
327016b0-6508-41d2-bce0-c1724cb3d3e2    2       63175437-7d59-4851-b333-c96cb6545a86
858a817e-0ca2-473f-89d3-d5bdfc51968e    3       63175437-7d59-4851-b333-c96cb6545a86
da42ca85-179b-4873-b12e-32d549bf02b6    2       63175437-7d59-4851-b333-c96cb6545a86
~~~~

The results show the UUID of the image, the availability state and the
subscription UUID. The state value is a bitmap, 1 is subscribed, 2 means
its available in the current `Virtual Machine Image List`{.literal}s.
Now we will select an image for local caching.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### Selecting Images

Images can be selected by either UUID or Sha512 hash. This allows
explicit selection of images or by the sha512 from an old image.

Delete the subscription by image.

~~~~ {.programlisting}
[user] $  vmlisub_image -D -u 327016b0-6508-41d2-bce0-c1724cb3d3e2
~~~~

Subscribe to an image.

~~~~ {.programlisting}
[user] $  vmlisub_image -a -u 327016b0-6508-41d2-bce0-c1724cb3d3e2
~~~~

Unsubscribe an image

~~~~ {.programlisting}
[user] $  vmlisub_image -r -u 327016b0-6508-41d2-bce0-c1724cb3d3e2
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### vmlisub\_cache

This application downloads images. By default it will download images,
check the sha512 hash of cached images and expire images from old
`Virtual Machine Image List`{.literal}s.

~~~~ {.programlisting}
[user] $  vmlisub_cache
INFO:vmlisub_sub.main:Defaulting DB connection to 'sqlite:///vmilsubscriber.db'
INFO:vmlisub_sub.main:Defaulting actions as 'expire', 'sha512' and 'download'.
INFO:vmlisub_sub.main:Defaulting cache-dir to 'cache'.
INFO:vmlisub_sub.main:Defaulting partial-dir to 'cache/partial'.
INFO:vmlisub_sub.main:Defaulting expired-dir to 'cache/expired'.
INFO:DownloadDir:Downloading '858a817e-0ca2-473f-89d3-d5bdfc51968e'.
INFO:CacheMan:moved file 858a817e-0ca2-473f-89d3-d5bdfc51968e
~~~~

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### vmlisub\_cache Event interface

Since this application suite is intended to be embedded in a larger
application and concerned with downloading and managing updates of VM
images into a cloud infrastructure, it is some times beneficial to have
an event interface so that applicatyions may embed these applications in
larger systems.

~~~~ {.programlisting}
[user] $  vmlisub_cache -x "/usr/bin/VmImageUpdateProcessor \$VMILS_EVENT_TYPE"
~~~~

The events interface launches a shell with a series of environment
variables. The event must process its command within 10 seconds or else
it will be sent a termination signal. See the following example:

~~~~ {.programlisting}
[user] $  vmlisub_cache -x 'env  ; exit 1'
~~~~

All Events have a type. This is given to the event handler by setting
the variable, VMILS\_EVENT\_TYPE with the following values
"AvailablePrefix", "AvailablePostfix", "ExpirePrefix" and
"ExpirePosfix".

"Available" events happen when a new image is validated, while "Expire"
events occur when an image i no longer the validated image. The "Prefix"
events occur before the file changes state, and the "Posfix" events
occur after the state change.

The following environment variables may be set by events:

-   VMILS\_EVENT\_TYPE
-   VMILS\_EVENT\_DC\_DESCRIPTION
-   VMILS\_EVENT\_DC\_IDENTIFIER
-   VMILS\_EVENT\_DC\_TITLE
-   VMILS\_EVENT\_HV\_HYPERVISOR
-   VMILS\_EVENT\_HV\_SIZE
-   VMILS\_EVENT\_HV\_URI
-   VMILS\_EVENT\_SL\_ARCH
-   VMILS\_EVENT\_SL\_CHECKSUM\_SHA512
-   VMILS\_EVENT\_SL\_COMMENTS
-   VMILS\_EVENT\_SL\_OS
-   VMILS\_EVENT\_SL\_OSVERSION
-   VMILS\_EVENT\_TYPE
-   VMILS\_EVENT\_FILENAME

These correspond to the variables within the
`Virtual Machine Image List`{.literal}.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### vmlisub\_cache Event Environment variables

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_TYPE

-   AvailablePrefix

    An image will be available soon as it is being attempted to be
    retrieved.

-   AvailablePostfix

    An image was successfully validated as being available and placed in
    the cache directory.

-   ExpirePrefix

    This image is will no longer be available in the cache directory.

-   ExpirePosfix

    This image is no longer in the cache directory.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_DC\_DESCRIPTION

The description text in the image.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_DC\_IDENTIFIER

Unique identifier of the image. Its suggested that image producers use
RFC 4122 UUID for `Virtual Machine Image List`{.literal} this allows
updating the list, and uniqueness.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_DC\_TITLE

Image Title.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_HV\_HYPERVISOR

Typically set to reflect the Virtualization technology values such as
"xen", "kvm".

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_HV\_SIZE

The Image Size

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_HV\_URI

The Original URI for the image

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_SL\_ARCH

The images architecture.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_SL\_CHECKSUM\_SHA512

The Images sha512 checksum.

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_SL\_COMMENTS

Comments added by the image author

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_SL\_OS

The Operating System the VM image contains

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_SL\_OSVERSION

The Operating System version

[[return to top](imagetransfer-software-vmlisub.shtml)]

###### VMILS\_EVENT\_FILENAME

The Image file name.

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Logging configuration

All scripts have a logging option. This is used to configure pythons
logging library. An example is shown below.

~~~~ {.programlisting}
[user] $  vmlisub_image -L /usr/share/doc/hepixvmilsubscriber/logger.conf -l
~~~~

Logging can be independently set up for each object to multiple
locations, and with different log levels.

[[return to top](imagetransfer-software-vmlisub.shtml)]

#### Environment Variables

Environment variables can be used to set default values but the command
line options will override any set environment options.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_RDBMS

Sets the path to the database. For example "sqlite:///vmilsubscriber.db"

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_EVENT

Sets the executions string. Command line options can be set as
enviroment variables just like the command line interface. Users of the
"sh shell" must protect the envroment variables from being substituted
by thier shell.

~~~~ {.programlisting}
[user] $  export VMILS_CACHE_EVENT="./myEventProcessor \$VMILS_EVENT_TYPE"
~~~~

An example of how to execute a command with an action command line.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_LOG\_CONF

Sets the path to the logging configuration file.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_DIR\_CERT

Sets the Path to the certificate authorities public keys, certificate
revocation lists and certificate name spaces.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_DIR\_CACHE

Path used by ’vmlisub\_endorser’ to store verified VM images.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_DIR\_DOWNLOAD

Path used by ’vmlisub\_endorser’ to download VM images before VM image
integrity is checked.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_DIR\_EXPIRE

Path used by ’vmlisub\_endorser’ to store VM images when they are no
longer endorsed.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_ACTION\_DOWNLOAD

Instructs ’vmlisub\_endorser’ to download the latest VM images and check
integrity.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_ACTION\_CHECK

Instructs ’vmlisub\_endorser’ check integrity for all currently stored
VM images.

[[return to top](imagetransfer-software-vmlisub.shtml)]

##### VMILS\_CACHE\_ACTION\_EXPIRE

Instructs ’vmlisub\_endorser’ to expire stored VM images that are no
longer endorsed.

[[return to top](imagetransfer-software-vmlisub.shtml)]

### To Do (16-05-2012)

-   Only message authenticity is checked, does not yet check
    authenticity of transport.

While it does check the authenticity of the message using X509, at the
moment the authenticity of the host is unchecked. For the
programmability it would be far simpler to use x509 certificates to
check the host server. In terms of deployment it would be far easier
just to check any host key mechanism, as this is sufficient.

* * * * *

  -------------------------------------------------------------------------- ----------------------------------------------- ---------------------------------------------
  [Prev](imagetransfer-software-subscriber.shtml)                            [Up](imagetransfer-software-subscriber.shtml)    [Next](imagetransfer-software-site.shtml)
  Chapter 10. `Virtual Machine Image List`{.literal} Subscribing Software    [Home](../index.shtml)                           Chapter 11. Site Image Management Software
  -------------------------------------------------------------------------- ----------------------------------------------- ---------------------------------------------


