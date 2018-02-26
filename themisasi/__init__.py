#!/usr/bin/env python
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
from pathlib import Path
from datetime import datetime
from numpy import array
import re
from dateutil.parser import parse
from spacepy import pycdf
#
from sciencedates import forceutc
#
fullthumb='f' #f for full, t for thumb


def readthemis(fn:Path, treq:datetime=None):
    """read THEMIS ASI camera data"""
    if pycdf is None:
        raise ImportError('you need spacepy.pycdf and CDF installed. \n  https://scivision.co/installing-spacepy-with-anaconda-python-3')

    fn = Path(fn).expanduser()


#%% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)',fn.name)
    site = m.group(0)
#%% plot,save video
    with pycdf.CDF(str(fn)) as f:
        try: #full
            T = forceutc(f[f'thg_asf_{site}_epoch'][:])
            #epoch0 = f['thg_as{}_{}_epoch0'.format(fullthumb,site)]
            imgs = f[f'thg_asf_{site}'][:] # slicing didn't work for some reason with Pycdf 0.1.5
        except KeyError:
            T = forceutc(f[f'thg_ast_{site}_time'][:])
            imgs = f[f'thg_ast_{site}'][:]

        if treq is not None:
            if isinstance(treq[0], str):
                treq = [parse(t) for t in treq]
            assert isinstance(treq[0],datetime)

            if isinstance(T[0], float):
                T=array([datetime.utcfromtimestamp(t) for t in T])

            tind = (treq[0] <= T) & (T <= treq[1])
            return imgs[tind,:,:], T[tind],site

        else:
            return imgs[:], T[:], site


#def calmulti(flist):
#    """
#    read plate scale data of other cameras and store in lists for iteration
#    use lists because other cameras might each have unique pixel counts or configurations
#    """
#    if isinstance(flist,str): flist = [flist]
#    flist = [Path(f).expanduser() for f in flist]
#
#    az = []; el = [] #each image might be a different size
#    lla = empty((len(flist),3))
#    for i,f in enumerate(flist):
#        a,e,l,x,y = calread(f)
#        az.append(a); el.append(e); lla[i,:] = l
#
#    return az,el,lla

