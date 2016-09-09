import logging
from numpy import mgrid,sin,radians
#
from pymap3d import enu2aer,geodetic2enu,aer2enu
from pymap3d.vdist import vdist
from histutils.findnearest import findClosestAzel
#
from .calread import calread
from .plots import plotjointazel

def mergefov(ofn,wlla,waz,wel,wrows,wcols,narrowflist,projalt,site=''):
    """
    inputs:
    -------
    ofn: filename to save (optional)
    wlla: wide FOV lat,lon,alt (deg,deg,meters)
    waz: wide FOV azimuth map 2-D (deg)
    wel: wide FOV elevation map 2-D (deg)
    wrows, wcols: optional (None,None) or 2-D indices of pixels
    narrowflist: list of narrow cal files
    projalt: projection altitude METERS
    site: optional text label
    """
    if projalt<1e3:
        logging.warning('this function expects meters, you picked projection altitude {} km'.format(projalt/1e3))

    if wrows is None and wcols is None:
        wrows,wcols = mgrid[:waz.shape[0], :waz.shape[1]]

    rows=[]; cols=[]
    for f in narrowflist:
#%% load plate scale for narrow camera
        oaz,oel,olla,oC,oR = calread(f)
#%% print distance from wide camera to narrow camera (just for information)
        print('distance: narrow FOV camera to {}:  {:.1f} meters'.format(site,vdist(wlla['lat'],wlla['lon'],
                                                                                    olla['lat'],olla['lon'])))
#%% select edges of narrow FOV
        oaz,oel = getedgeazel(oaz,oel)
#%% use ENU for both sites (thanks J. Swoboda)
#    wenu = array([0,0,0]) #make ASI at ENU origin
        oe,on,ou = geodetic2enu(olla['lat'],olla['lon'],olla['alt_m'],
                                wlla['lat'],wlla['lon'],wlla['alt_m'])
#%% find the ENU of narrow FOV pixels at 110km from narrow FOV
    # FIXME if rectangular camera chip, use nans perhaps with square array
        ope ,opn, opu = aer2enu(oaz,oel,projalt/sin(radians(oel)))   #cos(90-x) = sin(x)
#%% find az,el to narrow FOV from ASI FOV
        wpaz,wpel,_ = enu2aer(ope-oe, opn-on, opu-ou)
#%% nearest neighbor brute force
        print('finding nearest neighbors {} (takes 25 seconds per camera)'.format(f))
        r,c = findClosestAzel(waz,wel,wpaz,wpel,True)
        rows.append(r); cols.append(c)
#%% plot joint az/el contours
        plotjointazel(waz,wel,rows,cols,wrows,wcols,ofn,projalt)

    return rows,cols

def getedgeazel(az,el):
    # Use list because image may not be square
    Az = []; El=[]
    Az.append(az[0, :]); El.append(el[0, :])
    Az.append(az[-1,:]); El.append(el[-1,:])
    Az.append(az[:, 0]); El.append(el[:, 0])
    Az.append(az[:,-1]); El.append(el[:,-1])

    return Az,El