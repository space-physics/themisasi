#!/usr/bin/env python
"""
Plot time series for pixel(s) chosen by az/el

PlotThemisPixels ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf \
    ~/data/themis/thg_l2_asc_fykn_19700101_v01.cdf \
    -az 65 70 -el 48 68

PlotThemisPixels tests/thg_l1_ast_gako_20110505_v01.cdf \
    tests/thg_l2_asc_fykn_19700101_v01.cdf \
    -az 65 70 -el 48 68
"""
import os
import logging
from argparse import ArgumentParser
import numpy as np
import xarray
import themisasi as ta
import histutils.findnearest as fn
import pymap3d as pm
from typing import Tuple
try:
    import themisasi.plots as tap
    from matplotlib.pyplot import show
except ImportError as e:
    logging.error(f'not showing plots due to {e}')
    tap = None


def getimgind(imgs: xarray.Dataset, lla: Tuple[float, float, float],
              az: float, el: float) -> np.ndarray:

    if az is not None and el is not None:
        ind = fn.findClosestAzel(imgs.az, imgs.el, az, el)
    elif lla is not None:
        az, el, _ = pm.geodetic2aer(lla[0], lla[1], lla[2]*1000,
                                    imgs.lat, imgs.lon, imgs.alt_m)

        ind = fn.findClosestAzel(imgs.az, imgs.el, az, el)

    ind = np.unique(np.transpose(ind), axis=0)

    assert ind.ndim == 2
    assert ind.shape[1] == 2  # row, column

    return ind


def feedback(imgs: xarray.Dataset, ind: np.ndarray, lla: Tuple[float, float, float]):
    az = imgs.az[ind[:, 0], ind[:, 1]].values.squeeze()
    el = imgs.el[ind[:, 0], ind[:, 1]].values.squeeze()

    alt_m = lla[2]*1000 if lla is not None else 100e3

    plat, plon, palt_m = pm.aer2geodetic(az, el, alt_m / np.sin(np.radians(el)),
                                         imgs.lat, imgs.lon, imgs.alt_m)

    print(f'Using az, el {az}, {el}')
    print(f'Using projected lat,lon, alt [km]  {plat} {plon}  {palt_m}')


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI (or cal, if only argument) file to play')
    p.add_argument('cal', help='ASI az/el cal file to read')
    p.add_argument('-az', help='azimuth(s) to plot (degrees)', type=float, nargs='+')
    p.add_argument('-el', help='elevation(s) to plot (degrees)', type=float, nargs='+')
    p.add_argument('-lla', help='latitude, longitude, altitude [km] projection',
                   type=float, nargs=3)
    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    p.add_argument('-v', '--verbose', action='store_true')
    P = p.parse_args()

    imgs = ta.load(P.asifn, P.treq, P.cal)

    if P.verbose:
        tap.plotazel(imgs)
# %% select nearest neighbor
    ind = getimgind(imgs, P.lla, P.az, P.el)

    feedback(imgs, ind, P.lla)

    dat = np.empty((imgs.time.size, ind.shape[0]), dtype=imgs['imgs'].dtype)
    for i, j in enumerate(ind):
        dat[:, i] = imgs['imgs'][:, j[0], j[1]]

    if tap is not None:
        tap.plottimeseries(dat, imgs.time)

        if 'TRAVIS' not in os.environ or not os.environ['TRAVIS']:
            show()


if __name__ == '__main__':
    main()
