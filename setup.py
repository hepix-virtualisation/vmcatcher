from hepixvmlis.__version__ import version
from sys import version_info
if version_info < (2, 6):
	from distutils.core import setup
else:
	try:
        	from setuptools import setup, find_packages
	except ImportError:
        	from ez_setup import use_setuptools
        	use_setuptools()
        	from setuptools import setup, find_packages


setup(name='hepixvmilsubscriber',
    version=version,
    description="VM Image list subscribing tool.",
    long_description="""This application attempts to be the equivalent of a modern Linux package update
manager but for lists of virtual machines signed with x509. It uses a database
back end, and caches available image lists.""",
    author="O M Synge",
    author_email="owen.synge@desy.de",
    license='Apache License (2.0)',
    install_requires=[
       "M2Crypto>=0.16",
        ],
    url = 'https://github.com/hepix-virtualisation/hepixvmilsubscriber',
    packages = ['hepixvmlis'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research'
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],

    scripts=['vmlisub_image','vmlisub_sub','vmlisub_cache','vmlisub_endorser'],
    data_files=[('/usr/share/doc/hepixvmilsubscriber-%s' % (version),['README.md','LICENSE','logger.conf','ChangeLog','vmlisub_eventHndlExpl'])]
    )
