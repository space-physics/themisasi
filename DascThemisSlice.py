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
import logging
import xarray
import numpy as np
from matplotlib.pyplot import figure, show
#
from pymap3d.haversine import anglesep
import themisasi.fov as taf
import themisasi as ta
import themisasi.plots as tap
import dascutils.io as dio

def line2plane(cam:xarray.Dataset) -> xarray.Dataset:
    """
    previously, you find the row, col pixels along the line from the other camera to magnetic zenith.
    In this function, you find the indices of the plane passing through that line and both cameras.

    Inputs:
    -------
    row: row indices of line
    col: column indices of line
    nPlane: number of samples (pixels) to take for plane. If the plane is horizontal in the images, it would be approximately the number of x-pixels.
            If diagonal, it would be about sqrt(2)*Nx. If less, the image is sampled more sparsely, which is in effect recducing the resolution of the image.
            This parameter is not critical.
    """
# %% linear regression
    polycoeff = np.polyfit(cam['cols'], cam['rows'], deg=3, full=False)
# %% columns (x)  to cut from picture (have to pick either rows or cols, arbitrarily I use cols)
    # NOT range, NEED dtype= for arange api

# %% rows (y) to cut from picture
    cam['cutrow'] = np.rint(np.polyval(polycoeff, cam['cutcol'])).astype(int)
    assert (cam['cutrow'] >= 0).all() and (cam['cutrow'] < cam.y.size).all(),'impossible least squares fit for 1-D cut\n is your video orientation correct? are you outside the FOV?'

    # DONT DO THIS: cutrow.clip(0,self.supery,cutrow)
# %% angle from magnetic zenith corresponding to those pixels
    anglesep_deg = anglesep(cam.Bel, cam.Baz,
                            cam.el.values[cam.cutrow, cam.cutcol],  # NEED .values or you'll get 2-D instead of 1-D!
                            cam.az.values[cam.cutrow, cam.cutcol])

    if cam.verbose:
        ax = figure().gca()
        ax.plot(cam.cutcol, anglesep_deg, label='angle_sep from MZ')
        ax.plot(cam.cutcol, cam.el.values[cam.cutrow, cam.cutcol], label='elevation angle [deg]')
        ax.legend()

    assert anglesep_deg.ndim==1
    if not np.isfinite(anglesep_deg).all():
        logging.error(f'did you pick areas outside the {cam.filename} FOV?')
# %% assemble angular distances from magnetic zenith--these are used in the tomography algorithm
    cam['angle_deg'], cam['angleMagzenind'] = sky2beam(anglesep_deg, cam.cutcol.size)

    return cam


def sky2beam(anglesep_deg, Ncol:int):
        angle_deg = np.empty(Ncol, float)
        MagZenInd = anglesep_deg.argmin() # whether minimum angle distance from MZ is slightly positive or slightly negative, this should be OK

        angle_deg[MagZenInd:] = 90. + anglesep_deg[MagZenInd:]
        angle_deg[:MagZenInd] = 90. - anglesep_deg[:MagZenInd]
#%% LSQ
        col = np.arange(Ncol, dtype=int)
        polycoeff = np.polyfit(col,angle_deg,deg=1,full=False)

        return np.polyval(polycoeff,col), MagZenInd


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description = 'register/plot other camera FOV onto Themis FOV')
    p.add_argument('themiscal',help='ASI calibration')
    p.add_argument('dasccal',help='DASC cal',nargs=3)
    p.add_argument('-o','--ofn',help='write output plot')
    p.add_argument('-v','--verbose',action='store_true')
    p = p.parse_args()

# %% load az/el data
    themis = ta.loadcal(p.themiscal)
    if themis.site == 'gako':
        themis.attrs['Baz'] = 21.028
        themis.attrs['Bel'] = 75.816
        themis.attrs['Bepoch'] = '2010-01-01'
        themis.attrs['verbose'] = False
        themis.attrs['srpts'] = np.logspace(5, 6.9, 40)
        themis['cutcol'] = np.arange(50, themis.x.size-75,1, dtype=int)

    dasc = dio.load(*p.dasccal)
    if not 'lat' in dasc.attrs:
        dasc.attrs['lat'] = 65.126
        dasc.attrs['lon'] = -147.479
        dasc.attrs['alt_m'] = 200.
        dasc.attrs['Baz'] = 21.145  # Baz = declination
        dasc.attrs['Bel'] = 77.464  # Bel = inclination
        dasc.attrs['Bepoch'] = '2010-01-01'
        dasc.attrs['verbose'] = False
        dasc.attrs['srpts'] = np.logspace(4.6, 7.5, 40) #np.linspace(10**4.6,10**6.8,40) #np.logspace(4.6, 6.4, 40)
        dasc['cutcol'] = np.arange(75, dasc.x.size-100,1, dtype=int)
# %% extract common 2-D slice (plane)
    themis, dasc = taf.mergefov(themis, dasc, projalt=110e3, method='MZslice') #paint HiST field of view onto Themis
    themis = line2plane(themis)
    dasc = line2plane(dasc)
# %% plot slice pixel mask
    tap.jointazel(themis, p.ofn, 'Themis Gakona slice toward DASC and magnetic zenith')
    tap.jointazel(dasc, p.ofn,'DASC Poker Flat slice toward Themis Gakona and magnetic zenith')

    show()