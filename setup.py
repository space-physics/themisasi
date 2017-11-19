#!/usr/bin/env python
req = ['nose','numpy',
       'sciencedates',
          'spacepy']
# %%
from setuptools import setup, find_packages

setup(name='themisasi',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/themisasi',
      description='reads and plots THEMIS ASI video data of aurora.',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
      ],
      install_requires=req,
      python_requires='>=3.6',
      extras_requires={'plot':['astrometry_azel','matplotlib',],
                       'fov':['histutils','pymap3d','netcdf4','h5py','scipy',]}
	  )

