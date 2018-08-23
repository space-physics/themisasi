#!/usr/bin/env python
"""
UAF DASC with THEMIS GBO ASI FOV: Take a slice

The API to take the slice is very old code with a cumbersome, awkward API.
I have started by making a monkey-patched use of this API.
If the project proceeds, I would perhaps redo the API much more cleanly.

./DascThemisFOV.py ~/data/themis/themis_skymap_gako_20070401.sav ~/data/dasc/PKR_DASC_0000_20080326_070857.000.FITS \
     ../dascutils/cal/PKR_DASC_20110112_AZ_10deg.fits ../dascutils/cal/PKR_DASC_20110112_EL_10deg.fits

DASC coord: 65.1260, -147.479
DASC exposure: 1 sec.
"""
from argparse import ArgumentParser
import numpy as np
import themisasi.fov as taf
import themisasi.io as tio
import themisasi.plots as tap
import dascutils.io as dio
try:
    from matplotlib.pyplot import show
except ImportError:
    show = None


def main():
    p = ArgumentParser(description='register/plot other camera FOV onto Themis FOV')
    p.add_argument('themiscal', help='ASI calibration')
    p.add_argument('dasccal', help='DASC cal', nargs=3)
    p.add_argument('-o', '--ofn', help='write output plot')
    p.add_argument('-v', '--verbose', action='store_true')
    P = p.parse_args()

# %% load az/el data
    themis = tio.loadcal(P.themiscal)
    if themis.site == 'gako':
        themis.attrs['Baz'] = 21.028
        themis.attrs['Bel'] = 75.816
        themis.attrs['Bepoch'] = '2010-01-01'
        themis.attrs['verbose'] = False
        themis.attrs['srpts'] = np.logspace(5, 6.9, 40)
        themis['cutcol'] = np.arange(50, themis.x.size - 75, 1, dtype=int)

    dasc = dio.load(*P.dasccal)
    if 'lat' not in dasc.attrs:
        dasc.attrs['lat'] = 65.126
        dasc.attrs['lon'] = -147.479
        dasc.attrs['alt_m'] = 200.
        dasc.attrs['Baz'] = 21.145  # Baz = declination
        dasc.attrs['Bel'] = 77.464  # Bel = inclination
        dasc.attrs['Bepoch'] = '2010-01-01'
        dasc.attrs['verbose'] = False
        # np.linspace(10**4.6,10**6.8,40) #np.logspace(4.6, 6.4, 40)
        dasc.attrs['srpts'] = np.logspace(4.6, 7.5, 40)
        dasc['cutcol'] = np.arange(75, dasc.x.size - 100, 1, dtype=int)
# %% extract common 2-D slice (plane)
    # paint HiST field of view onto Themis
    themis, dasc = taf.mergefov(themis, dasc, projalt=110e3, method='MZslice')
    themis = taf.line2plane(themis)
    dasc = taf.line2plane(dasc)
    if show is None:
        return
# %% plot slice pixel mask
    tap.jointazel(
        themis, P.ofn, 'Themis Gakona slice toward DASC and magnetic zenith')
    tap.jointazel(
        dasc, P.ofn, 'DASC Poker Flat slice toward Themis Gakona and magnetic zenith')

    show()


if __name__ == '__main__':
    main()
