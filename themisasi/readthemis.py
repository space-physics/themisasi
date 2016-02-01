#!/usr/bin/env python3
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
from pathlib import Path
from datetime import datetime
from numpy import empty,sin,radians,flipud
import re
import h5py
from netCDF4 import Dataset
from dateutil.parser import parse
from scipy.io import readsav
from spacepy import pycdf
#
from pymap3d.coordconv3d import enu2aer,geodetic2enu,aer2enu
from histutils.findnearest import findClosestAzel
from .plots import plotjointazel
#
fullthumb='f' #f for full, t for thumb

def readthemis(fn,treq,odir):
    fn = Path(fn).expanduser()

    if odir: odir = Path(odir).expanduser()
#%% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)',fn.name)
    site = m.group(0)
#%% plot,save video
    with pycdf.CDF(str(fn)) as f:
        T = f['thg_as{}_{}_epoch'.format(fullthumb,site)][:]
        #epoch0 = f['thg_as{}_{}_epoch0'.format(fullthumb,site)]
        imgs = f['thg_as{}_{}'.format(fullthumb,site)][:] # slicing didn't work for some readon with Pycdf 0.1.5

        if treq:
            if isinstance(treq[0],str):
                treq = [parse(t) for t in treq]
            assert isinstance(treq[0],datetime)

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
        with readsav(str(fn),verbose=True) as h:
            az = h['skymap/full_azimuth'][:]
            el = h['skymap/full_elevation'][:]
            lla= [h['skymap/site_map_latitude'],
                  h['skymap/site_map_longitude'],
                  h['skymap/site_map_altitude']]
            x  = h['skymap/full_column'][:]
            y  = h['skymap/full_row'][:]
    elif fn.suffix=='.h5':
        with h5py.File(str(fn),'r',libver='latest') as h:
            az = h['az'].value
            el = h['el'].value
            lla= h['lla'].value
            x  = h['x'].value
            y  = h['y'].value
    elif fn.suffix == '.nc':
        with Dataset(str(fn),'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lla= h['lla'][:].squeeze()
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

def altfiducial(asifn,asicalfn,othercalfn,treq=None,odir=None,projalt=110e3):
    """
    asifn: image filename for ASI
    asicalfn: plate scale file for ASI
    othercalfn: plate scale for other camera
    projalt: projection altitude [m]


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
    if not isinstance(othercalfn,(tuple,list)):
        othercalfn=[othercalfn]
    #get ASI images
    imgs,t,site = readthemis(asifn,treq,odir)
#%% load plate scale for ASI
    waz,wel,wlla,wC,wR = calread(asicalfn)

    rows=[]; cols=[]
    for of in othercalfn:
#%% load plate scale for narrow camera and paint outline onto ASI image
        oaz,oel,olla,oC,oR = calread(of)
#%% select edges of narrow FOV
        oaz,oel = getedgeazel(oaz,oel)
#%% use ENU for both sites (thanks J. Swoboda)
#    wenu = array([0,0,0]) #make ASI at ENU origin
        oe,on,ou = geodetic2enu(olla[0],olla[1],olla[2],
                                wlla[0],wlla[1],wlla[2])
#%% find the ENU of narrow FOV pixels at 110km from narrow FOV
    # FIXME if rectangular camera chip, use nans perhaps with square array
        ope ,opn, opu = aer2enu(oaz,oel,projalt/sin(radians(oel)))   #cos(90-x) = sin(x)
#%% find az,el to narrow FOV from ASI FOV
        wpaz,wpel,_ = enu2aer(ope-oe, opn-on, opu-ou)
#%% nearest neighbor brute force
        print('finding nearest neighbors (takes 25 seconds per camera)')
        r,c = findClosestAzel(waz,wel,wpaz,wpel,True)
        rows.append(r); cols.append(c)
#%% plot joint az/el contours
        plotjointazel(waz,wel,rows,cols,wR,wC,asifn)

    return imgs,rows,cols,t,site,wR,wC

def getedgeazel(az,el):
    # Use list because image may not be square
    Az = []; El=[]
    Az.append(az[0, :]); El.append(el[0, :])
    Az.append(az[-1,:]); El.append(el[-1,:])
    Az.append(az[:, 0]); El.append(el[:, 0])
    Az.append(az[:,-1]); El.append(el[:,-1])

    return Az,El
