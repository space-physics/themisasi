from argparse import ArgumentParser

from .io import load
from .plots import plotasi, plotazel

"""
Playback THEMIS ASI videos
* optionally, save images to stack of PNGs

PlotThemis ~/data/themis/thg_l1_asf_fykn_2013041408_v01.cdf
"""


def cli():
    p = ArgumentParser(description=" reads THEMIS GBO ASI CDF files and plays high speed video")
    p.add_argument("path", help="directory THEMIS ASI video files are in")
    p.add_argument("site", help="THEMIS ASI site code e.g. fykn")
    p.add_argument("treq", help="time or start,stop time range requested", nargs="+")
    p.add_argument("-o", "--odir", help="write video to this directory")
    P = p.parse_args()

    imgs = load(P.path, site=P.site, treq=P.treq)
    # %% plot
    plotazel(imgs)

    plotasi(imgs, P.odir)
