#!/usr/bin/env python
import urllib.request
import tarfile
from pathlib import Path
import sys
import subprocess


R = Path('~').expanduser()
# %% download libcdf
url = 'https://spdf.sci.gsfc.nasa.gov/pub/software/cdf/dist/latest-release/cdf-dist-all.tar.gz'

ofn = R / url.split('/')[-1]

if not ofn.is_file():
    print(f'downloading {ofn}')
    urllib.request.urlretrieve(url, ofn)

print(f'extracting {ofn} to {R}')
with tarfile.open(ofn, mode="r") as f:
    f.extractall(R)
# %% build
if sys.platform.lower().startswith('linux'):
    cmd = 'make OS=linux ENV=gnu CURSES=yes FORTRAN=no UCOPTIONS=-O2 SHARED=yes -j4 all'.split(
        ' ')
elif sys.platform.lower().startswith('darwin'):
    cmd = 'make OS=macosx ENV=gnu CURSES=yes FORTRAN=no UCOPTIONS=-O2 SHARED=yes -j4 all'.split(
        ' ')
elif sys.platform.lower().startswith('windows'):
    raise ValueError(
        'Windows is not easy with SpacePy. Consider Windows Subsystem for Linux. Otherwise, see: \n https://pythonhosted.org/SpacePy/install_windows.html')
else:
    raise ValueError(f'I dont know how to install SpacePy on {sys.platform}')


cwd = list(R.glob('cdf*dist'))[0].resolve()
print(f'building CDF in {cwd} with command:')
print(cmd)
subprocess.check_call(cmd, cwd=cwd)
subprocess.check_call(['make', 'install'], cwd=cwd)  # no sudo

print('\nadd the following to ~/.bashrc\n')
print(f'. {cwd}/bin/definitions.B')
print('then reopen your Terminal and type the following to complete SpacePy install:')
print('pip install spacepy')
