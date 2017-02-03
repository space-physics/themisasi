#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)

setup(name='themisasi',
      packages=['themisasi'],
	  install_requires=['histutils','pymap3d','astrometry_azel'],
      dependency_links = [
        'https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
        'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
        'https://github.com/scienceopen/astrometry_azel/tarball/master#egg=astrometry_azel'
        ],
	  )

