#!/usr/bin/env python
"""
Plot THEMIS ASI in RA, DEC projection

ThemisRadec ~/data/2012-11-03/ gako 2012-11-03T06:30 ~/data/themis
"""
from argparse import ArgumentParser
import themisasi.io as tio
import themisasi.plots as tap


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('path', help='Themis ASI image file directory')
    p.add_argument('site', help='4 character site name e.g. gako')
    p.add_argument('treq', help='time or time range to load', nargs='+')
    p.add_argument('-c', '--calpath', help='path to calibration files', nargs='?')
    p.add_argument('-o', '--odir', help='output directory to write plots')
    P = p.parse_args()

    imgs = tio.load(P.path, site=P.site, treq=P.treq, calfn=P.calpath)
# %% plot
    tap.asi_radec(imgs, P.odir)

    print(imgs)


if __name__ == '__main__':
    main()
