#!/usr/bin/env python
from setuptools import setup

req = ['histutils','pymap3d','astrometry_azel','sciencedates',
       'nose','numpy','scipy','h5py','matplotlib','networkx','spacepy']

setup(name='themisasi',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/themisasi',
      description='reads and plots THEMIS ASI video data of aurora.',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      packages=['themisasi'],
	  install_requires=req,
#      setup_requires=['numpy'], #for spacepy, doesn't work
      extras_require={'spacepy':['spacepy'],'netcdf4':['netcdf4']},
	  )

