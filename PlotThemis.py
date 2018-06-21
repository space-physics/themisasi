#!/usr/bin/env python
"""
python PlotThemis.py ~/data/themis/thg_l1_asf_gako_2008032607_v01.cdf
"""
import themisasi as ta
import themisasi.plots as tap

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(
        description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI file to play')
    p.add_argument('cal', help='ASI az/el cal file to read', nargs='?')
    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    P = p.parse_args()

    imgs = ta.load(P.asifn, P.treq, P.cal)

    imgs = tap.plotasi(imgs, P.odir)
