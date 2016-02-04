#!/usr/bin/env python3

from themisasi.readthemis import plotthemis,readthemis,altfiducial

def playThemis(fn,t,site,odir):
    plotthemis(imgs,t,site,odir)


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description = ' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('asifn',help='ASI file to play')
    p.add_argument('--wcal',help='ASI az/el cal file to read')
    p.add_argument('--ncal',help='other camera (narrow FOV) cal file')
    p.add_argument('-t','--treq',help='time requested',nargs=2)
    p.add_argument('-o','--odir',help='write video to this directory')
    p.add_argument('-o','--ofn',help='write output to this movie file')
    p = p.parse_args()

    if p.wcal:
        altfiducial(p.asifn,p.wcal,p.ncal,p.treq,p.ofn) #paint HiST field of view onto Themis
    else:
        imgs,t,site = readthemis(p.asifn,p.treq,p.odir)
        try:
            imgs,t = playThemis(p.asifn,t,site,p.odir)
        except KeyboardInterrupt:
            pass