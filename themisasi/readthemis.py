#!/usr/bin/env python3
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
from pathlib import Path
from datetime import datetime
from numpy import empty,flipud,array
import re
import h5py
from dateutil.parser import parse
from scipy.io import readsav
try:
    from netCDF4 import Dataset
    from spacepy import pycdf
except ImportError:
    Dataset=pycdf=None
#
from histutils.fortrandates import forceutc
from .fov import mergefov
#
fullthumb='f' #f for full, t for thumb

def readthemis(fn,treq,odir):
    if pycdf is None:
        raise ImportError('you will need NetCDF, pycdf  https://scivision.co/installing-spacepy-with-anaconda-python-3')

    fn = Path(fn).expanduser()

    if odir: odir = Path(odir).expanduser()
#%% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)',fn.name)
    site = m.group(0)
#%% plot,save video
    with pycdf.CDF(str(fn)) as f:
        try: #full
            T = forceutc(f['thg_asf_{}_epoch'.format(site)][:])
            #epoch0 = f['thg_as{}_{}_epoch0'.format(fullthumb,site)]
            imgs = f['thg_asf_{}'.format(site)][:] # slicing didn't work for some reason with Pycdf 0.1.5
        except KeyError:
            T = forceutc(f['thg_ast_{}_time'.format(site)][:])
            imgs = f['thg_ast_{}'.format(site)][:]

        if treq:
            if isinstance(treq[0],str):
                treq = [parse(t) for t in treq]
            assert isinstance(treq[0],datetime)

            if isinstance(T[0],float):
                T=array([datetime.utcfromtimestamp(t) for t in T])

            tind = (treq[0]<=T) & (T<=treq[1])
            return imgs[tind,:,:], T[tind],site

        else:
            return imgs[:], T[:], site


def calread(fn):
    """
    reads data mapping themis gbo asi pixels to azimuth,elevation
    calibration data url is
    http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/
    """
    fn = Path(fn).expanduser()
    if fn.suffix=='.sav': # suppose it's THEMIS IDL
        h= readsav(str(fn),verbose=False) #readsav is not a context manager
        az, = h['skymap']['full_azimuth']
        el, = h['skymap']['full_elevation']
        lla= {'lat':   h['skymap']['site_map_latitude'],
              'lon':   h['skymap']['site_map_longitude'],
              'alt_m': h['skymap']['site_map_altitude']}
        x,  = h['skymap']['full_column']
        y,  = h['skymap']['full_row']
    elif fn.suffix=='.h5':
        with h5py.File(str(fn),'r',libver='latest') as h:
            az = h['az'].value
            el = h['el'].value
            lla= {'lat':h['lla'][0], 'lon':h['lla'][1], 'alt_m':h['lla'][2]}
            x  = h['x'].value
            y  = h['y'].value
    elif fn.suffix == '.nc':
        if Dataset is None:
            raise ImportError('you will need NetCDF  https://scivision.co/installing-spacepy-with-anaconda-python-3')
        with Dataset(str(fn),'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lla= {'lat':h['lla'][0], 'lon':h['lla'][1], 'alt_m':h['lla'][2]}
            x  = h['x'][:].astype(int)
            y  = flipud(h['y'][:]).astype(int)

    return az,el,lla,x,y

def calmulti(flist):
    """
    read plate scale data of other cameras and store in lists for iteration
    use lists because other cameras might each have unique pixel counts or configurations
    """
    if isinstance(flist,str): flist = [flist]
    flist = [Path(f).expanduser() for f in flist]

    az = []; el = [] #each image might be a different size
    lla = empty((len(flist),3))
    for i,f in enumerate(flist):
        a,e,l,x,y = calread(f)
        az.append(a); el.append(e); lla[i,:] = l

    return az,el,lla

def altfiducial(wfn,wcalfn,ncalflist,treq=None,odir=None,projalt=110e3):
    """
    wfn: image filename for ASI
    wcalfn: plate scale file for ASI
    ncalflist: plate scale for other camera
    projalt: projection altitude [meters]


    wa,wb,ella: az,el,lla (2d,2d,1d ndarrays) of widest FOV upon which to paint all other FOVs
    az,el,lla: (list,list,Nx3 ndarray) of all other FOVs

    lla is Nx3 of lat [deg], lon [deg], alt [meters]

    paint 110km altitude pixels on other camera
    I have az,el of each pixel and location of each camera
    I would like to take the outermost pixel boundary of the narrower FOV camera
    and paint that onto the FOV of the wider FOV camera at 110km altitude.

    That is, use the widest FOV camera as the basis upon which to draw 110km altitude projections of one or more other FOVs.

    One way to do so is find the ECEF x,y,z, at 110km altitude for narrow camera outer pixel
    boundary, then find the closest pixels in the wide FOV to those points.
    Remember, it can be (much) faster to brute force this calculation than to use
    k-d tree.

    NOTE: assume there are no NaNs in the narrow FOV camera,
    that the image fills the chip entirely, unlike ASI systems with dead regions around circular center
    """
    if not isinstance(ncalflist,(tuple,list)):
        ncalflist=[ncalflist]
    #get ASI images
    imgs,t,site = readthemis(wfn,treq,odir)
#%% load plate scale for ASI
    waz,wel,wlla,wcols,wrows = calread(wcalfn)
    #TODO ask Emma Spanswick how to reshape binned images, it's not completely trivial.
#    assert wcols.shape == imgs.shape[1:] == wrows.shape,'we do not handle binned images yet'


    rows,cols = mergefov(wfn,wlla,waz,wel,wrows,wcols,ncalflist,projalt,site)

    return imgs,rows,cols,t,site,wrows,wcols
