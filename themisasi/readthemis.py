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
import h5py
from dateutil.parser import parse
from scipy.io import readsav
from spacepy import pycdf
from matplotlib.pyplot import figure,draw,pause
from matplotlib.colors import LogNorm

fullthumb='f' #f for full, t for thumb

def readthemis(fn,treq,odir):
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
            return imgs[tind,...], T[tind],site

        else:
            return imgs[:], T[:], site


def calthemis(fn):
    """
    reads data mapping themis gbo asi pixels to azimuth,elevation
    """
    fn = Path(fn).expanduser()
    if fn.suffix=='.sav':
        with readsav(str(fn),verbose=True) as h:
            az = h['skymap/az']
            el = h['skymap/el']
            lla= h['skymap/lla']
    elif fn.suffix=='.h5':
        with h5py.File(str(fn),'r',libver='latest') as h:
            az = h['az']
            el = h['el']
            lla= h['lla']

    return az,el,lla




def plotthemis(imgs,T,site='',odir=None):
    fg = figure()
    ax = fg.gca()
    hi = ax.imshow(imgs[0],cmap='gray',origin='bottom',norm=LogNorm())     #sets contrast
    ht = ax.set_title('',color='g')
    #blank ticks
    ax.set_xticks([])
    ax.set_yticks([])

    for I,t in zip(imgs,T):
        hi.set_data(I)
        ht.set_text(str(t))
        draw(),pause(0.05)
        if odir:
            fg.savefig(str(odir/'Themis_{}_{}.png'.format(site,t.timestamp())),bbox_inches='tight',facecolor='k',dpi=150)
