#!/usr/bin/env python
"""
Plot time series for pixel(s) chosen by az/el

PlotThemisPixels ~/data/themis/ fykn 2011-01-06T17:00:00 -az 65 70 -el 48 68

PlotThemisPixels tests/ gako 2011-01-06T17:00:00 -az 65 70 -el 48 68
"""
from argparse import ArgumentParser
import numpy as np
import themisasi as ta
import themisasi.fov as taf
import themisasi.plots as tap
from matplotlib.pyplot import show


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('path', help='ASI data path')
    p.add_argument('site', help='site 4 character code e.g. gako')
    p.add_argument('treq', help='time (or time start,stop) requested', nargs='+')

    g = p.add_mutually_exclusive_group()
    p.add_argument('-az', help='azimuth(s) to plot (degrees)', type=float, nargs='+')
    g.add_argument('-el', help='elevation(s) to plot (degrees)', type=float, nargs='+')
    g.add_argument('-lla', help='latitude, longitude, altitude [km] projection',
                   type=float, nargs=3)

    p.add_argument('-o', '--odir', help='write video to this directory')
    p.add_argument('-v', '--verbose', action='store_true')
    P = p.parse_args()

    imgs = ta.load(P.path, site=P.site, treq=P.treq)

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
    ttxt = f'{imgs.filename}'
    tap.plottimeseries(dat, imgs.time, ttxt)

    show()


if __name__ == '__main__':
    main()
