#!/usr/bin/env python3
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
from pathlib import Path
from datetime import datetime
from numpy import nonzero
import re
from dateutil.parser import parse
from spacepy import pycdf
from matplotlib.pyplot import figure,draw,pause
from matplotlib.colors import LogNorm

fullthumb='f' #f for full, t for thumb

def playThemis(fn,treq,odir):
    fn = Path(fn).expanduser()
    if odir: odir = Path(odir).expanduser()
#%% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)',fn.name)
    site = m.group(0)
#%% plot,save video
    with pycdf.CDF(str(fn)) as f:
        T = f['thg_as{}_{}_epoch'.format(fullthumb,site)]
        #epoch0 = f['thg_as{}_{}_epoch0'.format(fullthumb,site)]
        imgs = f['thg_as{}_{}'.format(fullthumb,site)]

        if treq:
            if isinstance(treq[0],str):
                treq = [parse(t) for t in treq]
            assert isinstance(treq[0],datetime)
            tind = nonzero([treq[0]<=t<=treq[1] for t in T])[0]
        else:
            tind = range(len(T))

        plotmatplotlib(tind,imgs,T,odir)


def plotmatplotlib(tind,imgs,t,odir):
    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(imgs[0],cmap='gray',origin='bottom',norm=LogNorm())     #sets contrast
    ht = ax.set_title('',color='g')
    #blank ticks
    ax.set_xticks([])
    ax.set_yticks([])

    for i in tind:
        hi.set_data(imgs[i,...])
        ht.set_text(str(t[i]))
        draw(),pause(0.05)
        if odir:
            fg.savefig(str(odir/'Themis_{}_{}.png'.format(site,t[i])),bbox_inches='tight',facecolor='k',dpi=150)


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description = ' reads THEMIS GBO ASI CDF files and plays high speed video')
    p.add_argument('f',help='file to play')
    p.add_argument('-t','--treq',help='time requested',nargs=2)
    p.add_argument('-o','--odir',help='write video to this directory')
    p = p.parse_args()

    playThemis(p.f,p.treq,p.odir)