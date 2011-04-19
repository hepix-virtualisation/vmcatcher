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
    author="O M Synge",
    author_email="owen.synge@desy.de",
    install_requires=[
       "M2Crypto>=0.16",
        ],
    url = 'https://github.com/hepix-virtualisation/hepixvmilsubscriber',
    packages = ['hepixvmlis'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research'
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ],
    
    scripts=['vmlisub_image','vmlisub_sub'],
    data_files=[('/usr/share/doc/hepixvmilsubscriber',['README'])]
    )
