#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['numpy', 'spacepy',
                    'netcdf4', 'h5py', 'scipy>=0.17', 'xarray']
tests_require = ['pytest', 'coveralls', 'flake8', 'mypy']


setup(name='themisasi',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      version='0.7.0',
      url='https://github.com/scivision/themisasi',
      description='reads and plots THEMIS ASI video data of aurora.',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
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
      extras_require={'plot': ['matplotlib', 'seaborn'],
                      'fov': ['histutils', 'pymap3d', ],
                      'tests': tests_require},
      tests_require=tests_require,
      scripts=['setup_spacepy.py', 'DascThemisFOV.py', 'DascThemisSlice.py',
               'PlotThemis.py'],
      )
