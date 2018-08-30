#!/usr/bin/env python
"""
Playback THEMIS ASI videos
* optionally, save images to stack of PNGs

PlotThemis ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf
"""
from argparse import ArgumentParser
import themisasi as ta
import themisasi.plots as tap


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('path', help='directory THEMIS ASI video files are in')
    p.add_argument('site', help='THEMIS ASI site code e.g. fykn')
    p.add_argument('treq', help='time or start,stop time range requested', nargs='+')
    p.add_argument('-o', '--odir', help='write video to this directory')
    P = p.parse_args()

    imgs = ta.load(P.path, site=P.site, treq=P.treq)
# %% plot
    tap.plotazel(imgs)

    tap.plotasi(imgs, P.odir)


if __name__ == '__main__':
    main()
