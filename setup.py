from vmcatcher.__version__ import version
import sys

if sys.version_info < (2, 6):
    import sys
    print ("Please use a newer version of python")
    sys.exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
	try:
            from distutils.core import setup
	except ImportError:
            from ez_setup import use_setuptools
            use_setuptools()
            from setuptools import setup, find_packages

# we want this module for nosetests
try:
    import multiprocessing
except ImportError:
    # its not critical if this fails though.
    pass


setup(name='vmcatcher',
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
    url = 'https://github.com/hepix-virtualisation/vmcatcher',
    packages = ['vmcatcher',
        'vmcatcher/vmcatcher_subscribe',
        'vmcatcher/vmcatcher_image',
        'vmcatcher/vmcatcher_endorser',
        'vmcatcher/vmcatcher_cache',
        'vmcatcher/tests',
        ],
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

    scripts=['vmcatcher_image','vmcatcher_subscribe','vmcatcher_cache','vmcatcher_endorser'],
    data_files=[('share/doc/vmcatcher-%s' % (version),['README.md','LICENSE','logger.conf','ChangeLog','vmcatcher_eventHndlExpl'])],
    tests_require=[
        'coverage >= 3.0',
        'nose >= 0.10.0',
        'pytest',
        'mock',
        'SQLAlchemy >= 0.7.8',
        'M2Crypto',
    ],
    setup_requires=[
        'pytest',
        'nose >= 0.10.0',
        'SQLAlchemy >= 0.7.8',
        'M2Crypto',
    ],
    test_suite = 'nose.collector',
    )
