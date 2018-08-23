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
import logging
from argparse import ArgumentParser
import numpy as np
import themisasi.io as tio
import themisasi.fov as taf
import themisasi.plots as tap
try:
    from matplotlib.pyplot import show
except ImportError as e:
    logging.error(f'not showing plots due to {e}')
    show = None  # type: ignore


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI (or cal, if only argument) file to play')
    p.add_argument('cal', help='ASI az/el cal file to read')

    g = p.add_mutually_exclusive_group()
    p.add_argument('-az', help='azimuth(s) to plot (degrees)', type=float, nargs='+')
    g.add_argument('-el', help='elevation(s) to plot (degrees)', type=float, nargs='+')
    g.add_argument('-lla', help='latitude, longitude, altitude [km] projection',
                   type=float, nargs=3)

    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    p.add_argument('-v', '--verbose', action='store_true')
    P = p.parse_args()

    imgs = tio.load(P.asifn, P.treq, P.cal)

    if P.verbose:
        tap.plotazel(imgs)
# %% select nearest neighbor
    ind = taf.getimgind(imgs, P.lla, P.az, P.el)

    az, el, plat, plon, palt_m = taf.projected_coord(imgs, ind, P.lla)

    print(f'Using az, el {az}, {el}')
    print(f'Using projected lat,lon, alt [km]  {plat} {plon}  {palt_m}')

    dat = np.empty((imgs.time.size, ind.shape[0]), dtype=imgs['imgs'].dtype)
    for i, j in enumerate(ind):
        dat[:, i] = imgs['imgs'][:, j[0], j[1]]
# %% plot
    if show is None:
        return

    ttxt = f'{imgs.filename}'
    tap.plottimeseries(dat, imgs.time, ttxt)

    show()


if __name__ == '__main__':
    main()
