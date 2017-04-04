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

from setuptools.command.test import test as TestCommand
from nose.commands import nosetests

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

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
        'nose',
        'pytest',
        'mock',
        'SQLAlchemy >= 0.7.8',
        'M2Crypto',
    ],
    setup_requires=[
        'pytest',
        'nose',
        'SQLAlchemy >= 0.7.8',
        'M2Crypto',
    ],
    cmdclass = {
        'test': PyTest,
        'nosetests' : nosetests},
    )
