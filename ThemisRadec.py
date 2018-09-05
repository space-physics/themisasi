#!/usr/bin/env python
"""
Plot THEMIS ASI in RA, DEC projection

ThemisRadec ~/data/2012-11-03/thg_l1_asf_gako_2012110306_v01.cdf ~/data/themis/themis_skymap_gako_20070401.sav -t 2012-11-03T06:30
"""
from argparse import ArgumentParser
import themisasi.io as tio
import themisasi.plots as tap


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('path', help='Themis ASI image file directory')
    p.add_argument('site', help='4 character site name e.g. gako')
    p.add_argumetn('treq', help='time or time range to load')
    p.add_argument('-t', '--treq', help='time requested', nargs='+')
    p.add_argument('-o', '--odir', help='write video to this directory')
    P = p.parse_args()

    imgs = tio.load(P.path, site=P.site, treq=P.treq)
# %% plot
    tap.asi_radec(imgs, P.odir)

    print(imgs)


if __name__ == '__main__':
    main()
