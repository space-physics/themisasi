#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])

setup(name='themisasi',
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/themisasi',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      packages=['themisasi'],
	  install_requires=['histutils','pymap3d','astrometry_azel'],
      dependency_links = [
        'https://github.com/scienceopen/histutils/tarball/master#egg=histutils',
        'https://github.com/scienceopen/astrometry_azel/tarball/master#egg=astrometry_azel'
        ],
	  )

