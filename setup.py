#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--yes','--file','requirements.txt'])
except Exception as e:
    pass

with open('README.rst','r') as f:
	long_description = f.read()

setup(name='themisasi',
	  description='Utilities for working with THEMIS GBO ASI camera data',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/themisasi',
	  install_requires=['histutils','pymap3d','astrometry_azel'],
      dependency_links = [
        'https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
        'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
        'https://github.com/scienceopen/astrometry_azel/tarball/master#egg=astrometry_azel'
        ],
	  )

