#!/usr/bin/env python
"""
PlotThemis ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf
"""
from argparse import ArgumentParser
import themisasi as ta
import themisasi.plots as tap


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI (or cal, if only argument) file to play')
    p.add_argument('cal', help='ASI az/el cal file to read', nargs='?')
    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    P = p.parse_args()

    imgs = ta.load(P.asifn, P.treq, P.cal)

    tap.plotazel(imgs)

    tap.plotasi(imgs, P.odir)


if __name__ == '__main__':
    main()
