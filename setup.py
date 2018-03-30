#!/usr/bin/env python
install_requires = ['numpy','spacepy','netcdf4','h5py', 'scipy',
                    'sciencedates']
tests_require=['pytest','nose','coveralls']
# %%
from setuptools import setup, find_packages

setup(name='themisasi',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      version='0.5.0',
      url='https://github.com/scivision/themisasi',
      description='reads and plots THEMIS ASI video data of aurora.',
      long_description=open('README.rst').read(),
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Science/Research',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3.7',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      ],
      install_requires=install_requires,
      python_requires='>=3.6',
      extras_require={'plot':['matplotlib','seaborn'],
                       'fov':['histutils','pymap3d',],
                       'tests':tests_require},
      tests_require=tests_require,
	  )

