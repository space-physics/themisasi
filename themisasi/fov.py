import logging
from numpy import mgrid,sin,radians
#
from pymap3d import enu2aer,geodetic2enu,aer2enu
from pymap3d.vincenty import vdist
from histutils.findnearest import findClosestAzel
#
from . import readthemis
from .calread import calread
from .plots import plotjointazel


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
        logging.warning(f'this function expects meters, you picked projection altitude {projalt/1e3} km')

    if wrows is None and wcols is None:
        wrows,wcols = mgrid[:waz.shape[0], :waz.shape[1]]

    rows=[]; cols=[]
    for f in narrowflist:
#%% load plate scale for narrow camera
        oaz,oel,olla,oC,oR = calread(f)
#%% print distance from wide camera to narrow camera (just for information)
        print(f"distance: narrow FOV camera to {site}:  {vdist(wlla['lat'],wlla['lon'],olla['lat'],olla['lon'])[0]:.1f} meters")
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
        print(f'finding nearest neighbors {f} (takes 25 seconds per camera)')
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

