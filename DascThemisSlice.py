#!/usr/bin/env python
"""
UAF DASC with THEMIS GBO ASI FOV: Take a slice

The API to take the slice is very old code with a cumbersome, awkward API.
I have started by making a monkey-patched use of this API. 
If the project proceeds, I would perhaps redo the API much more cleanly.

./DascThemisFOV.py ~/data/themis/themis_skymap_gako_20070401.sav ~/data/dasc/PKR_DASC_0000_20080326_070857.000.FITS ../dascutils/cal/PKR_DASC_20110112_AZ_10deg.fits ../dascutils/cal/PKR_DASC_20110112_EL_10deg.fits

DASC coord: 65.1260, -147.479
DASC exposure: 1 sec.
"""
from pathlib import Path
import themisasi.fov as taf
import themisasi as ta
import dascutils.io as dio
import themisasi.plots as tap
from matplotlib.pyplot import show

class Sim():
    
    def __init__(self):
        self.raymap = 'astrometry'
        self.realdata = True
        self.realdatapath = Path('~/data').expanduser()
        


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description = 'register/plot other camera FOV onto Themis FOV')
    p.add_argument('themiscal',help='ASI calibration')
    p.add_argument('dasccal',help='DASC cal',nargs=3)
    p.add_argument('-o','--ofn',help='write output plot')
    p = p.parse_args()

# %% load az/el data
    themis = ta.loadcal(p.themiscal)
    if themis.site == 'gako':
        themis.attrs['Baz'] = 21.028
        themis.attrs['Bel'] = 75.816
    
    dasc = dio.load(*p.dasccal)
    if not 'lat' in dasc.attrs:
        dasc.attrs['lat'] = 65.126
        dasc.attrs['lon'] = -147.479
        dasc.attrs['alt_m'] = 200.
        dasc.attrs['Baz'] = 21.145  # Baz = declination
        dasc.attrs['Bel'] = 77.464  # Bel = inclination
# %% extract common 2-D slice (plane)
    themis, dasc = taf.mergefov(themis, dasc, projalt=110e3, method='MZslice') #paint HiST field of view onto Themis
# %% plot slice pixel mask
    tap.jointazel(themis, p.ofn, 'Themis Gakona slice toward DASC and magnetic zenith')

    show()