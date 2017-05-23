#!/usr/bin/env python
req = ['nose','numpy','scipy','h5py','matplotlib','networkx','netcdf4']
pipreq = ['histutils','pymap3d','astrometry_azel','sciencedates',
          'spacepy']
          
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup


setup(name='themisasi',
      packages=['themisasi'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/themisasi',
      description='reads and plots THEMIS ASI video data of aurora.',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
	  )

