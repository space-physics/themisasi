import logging
from pathlib import Path
import xarray
import numpy as np
#
from pymap3d import enu2aer,geodetic2enu,aer2enu
from pymap3d.vincenty import vdist
from histutils.findnearest import findClosestAzel
#
from .plots import plotjointazel


def mergefov(w0:xarray.Dataset, w1:xarray.Dataset, projalt:float=110e3, ofn:Path=None, fovrow:int=None):
    """
    inputs:
    -------
    w0: wide FOV data, particularly az/el
    w1: other camera FOV data contained in w0
    projalt: projection altitude METERS
    ofn: plot filename
    fovrow: to vastly speedup intiial overlap exploration, pick row(s) of pixels to examing--it could take half an hour + otherwise.

    find the ECEF x,y,z, at 110km altitude for narrow camera outer pixel
    boundary, then find the closest pixels in the wide FOV to those points.
    Remember, it can be (much) faster to brute force this calculation than to use
    k-d tree.

    """
    if projalt<1e3:
        logging.warning(f'this function expects meters, you picked projection altitude {projalt/1e3} km')

#%% print distance from wide camera to narrow camera (just for information)
    print(f"intercamera distance with {w0.site}:  {vdist(w0.lat,w0.lon, w1.lat,w1.lon)[0]/1e3:.1f} kilometers")
#%% ENU projection from cam0 to cam1
    e1,n1,u1 = geodetic2enu(w1.lat, w1.lon, w1.alt_m,
                            w0.lat, w0.lon, w0.alt_m)
#%% find the ENU of narrow FOV edge pixels at 110km from narrow FOV
    if fovrow is not None:
        az1 = w1['az'][fovrow,:]
        el1 = w1['el'][fovrow,:]
    else:
        az1,el1 = getedgeazel(w1['az'], w1['el'])

    slantrange = np.ma.masked_invalid(projalt / np.sin(np.radians(el1.values)))    # csc(x) = 1/sin(x)
    assert (slantrange >= projalt).all(), 'slantrange must be >= projection altitude'

    e0, n0, u0 = aer2enu(az1.values, el1.values, slantrange)
#%% find az,el to narrow FOV from ASI FOV
    az0,el0,_ = enu2aer(e0-e1, n0-n1, u0-u1)
    assert (el0 >= 0).all(), 'FOVs may not overlap, negative elevation from cam0 to cam1'
#%% nearest neighbor brute force
    rows,cols = findClosestAzel(w0['az'].values, w0['el'].values, az0, el0)
#%% plot joint az/el contours
    plotjointazel(w0, rows,cols, ofn)

    return rows,cols


def getedgeazel(az,el):
    # Use list because image may not be square
    Az = []; El=[]
    Az.append(az[0, :]); El.append(el[0, :])
    Az.append(az[-1,:]); El.append(el[-1,:])
    Az.append(az[:, 0]); El.append(el[:, 0])
    Az.append(az[:,-1]); El.append(el[:,-1])

    if np.isnan(Az).all() or np.isnan(El).all():
        raise ValueError('no FOV overlap found')

    return Az,El

