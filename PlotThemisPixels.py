#!/usr/bin/env python
"""
Plot time series for pixel(s) chosen by az/el

PlotThemisPixels ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf \
    !/data/themis/thg_l2_asc_fykn_19700101_v01.cdf \
    -az 65 70 -el 48 68
"""
from argparse import ArgumentParser
import numpy as np
import themisasi as ta
import themisasi.plots as tap
import histutils.findnearest as fn
from matplotlib.pyplot import show


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI (or cal, if only argument) file to play')
    p.add_argument('cal', help='ASI az/el cal file to read')
    p.add_argument('-az', help='azimuth(s) to plot (degrees)', type=float, nargs='+')
    p.add_argument('-el', help='elevation(s) to plot (degrees)', type=float, nargs='+')
    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    p.add_argument('-v', '--verbose', action='store_true')
    P = p.parse_args()

    imgs = ta.load(P.asifn, P.treq, P.cal)

    if P.verbose:
        tap.plotazel(imgs)
# %% select nearest neighbor
    ind = fn.findClosestAzel(imgs.az, imgs.el, P.az, P.el)
    ind = np.unique(np.transpose(ind), axis=0)

    dat = np.empty((imgs.time.size, ind.shape[0]), dtype=imgs['imgs'].dtype)
    for i, j in enumerate(ind):
        dat[:, i] = imgs['imgs'][:, j[0], j[1]]

    tap.plottimeseries(dat, imgs.time)

    show()


if __name__ == '__main__':
    main()
