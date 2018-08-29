#!/usr/bin/env python
"""
UAF DASC FOV overlaid on THEMIS GBO ASI FOV

./DascThemisFOV.py ~/data/themis/themis_skymap_gako_20070401.sav ../dascutils/tests/PKR_DASC_0428_20151007_082305.930.FITS \
       ../dascutils/cal/PKR_DASC_20110112_AZ_10deg.fits ../dascutils/cal/PKR_DASC_20110112_EL_10deg.fits
"""
from argparse import ArgumentParser
import themisasi.plots as tap
import themisasi.fov as taf
import themisasi.io as tio
import dascutils.io as dio
from matplotlib.pyplot import show


def main():
    p = ArgumentParser(description='register/plot other camera FOV onto Themis FOV')
    p.add_argument('themiscal', help='ASI calibration')
    p.add_argument('dasccal', help='DASC cal', nargs=3)
    p.add_argument('-o', '--ofn', help='write output plot')
    P = p.parse_args()

# %% load data
    themis = tio.loadcal(P.themiscal)
    dasc = dio.load(*P.dasccal)
# %% merge FOV
    # paint HiST field of view onto Themis
    themis, dasc = taf.mergefov(themis, dasc, projalt=110e3, method='perimeter')
# %% plot joint az/el contours
    tap.jointazel(themis, P.ofn, 'Themis Gakona overlaid on Poker Flat ASI')

    show()


if __name__ == '__main__':
    main()
