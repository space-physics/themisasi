#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass

setup(name='themisasi',
      packages=['themisasi'],
	  description='Utilities for working with THEMIS GBO ASI camera data',
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/themisasi',
	  install_requires=['pathlib2',
                        'histutils','pymap3d','astrometry_azel'],
      dependency_links = [
        'https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
        'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
        'https://github.com/scienceopen/astrometry_azel/tarball/master#egg=astrometry_azel'
        ],
	  )

