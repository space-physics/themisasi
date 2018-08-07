#!/usr/bin/env python
"""
Playback THEMIS ASI videos
* optionally, save images to stack of PNGs

PlotThemis ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf
"""
import logging
from argparse import ArgumentParser
import themisasi.io as tio
try:
    import themisasi.plots as tap
except ImportError as e:
    logging.error(f'not showing plots due to {e}')
    tap = None  # type: ignore


def main():
    p = ArgumentParser(description=' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn', help='ASI (or cal, if only argument) file to play')
    p.add_argument('cal', help='ASI az/el cal file to read', nargs='?')
    p.add_argument('-t', '--treq', help='time requested', nargs=2)
    p.add_argument('-o', '--odir', help='write video to this directory')
    P = p.parse_args()

    imgs = tio.load(P.asifn, P.treq, P.cal)
# %% plot
    if tap is None:
        return

    tap.plotazel(imgs)

    tap.plotasi(imgs, P.odir)


if __name__ == '__main__':
    main()
