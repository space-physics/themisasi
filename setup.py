#!/usr/bin/env python
from setuptools import setup

req = ['histutils','pymap3d','astrometry_azel','sciencedates',
       'nose','numpy','scipy','h5py','matplotlib','networkx']

setup(name='themisasi',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/themisasi',
      description='reads and plots THEMIS ASI video data of aurora. If you do not have SpacePy, see https://www.scivision.co/installing-spacepy-with-anaconda-python-3/ to install it.',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
        dependency_links = [
        'https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
        'https://github.com/scienceopen/astrometry_azel/tarball/master#egg=astrometry_azel'
        ],
      packages=['themisasi'],
	  install_requires=req,

	  )

