import logging
import xarray
import numpy as np
import scipy.ndimage as ndi
#
from pymap3d import enu2aer,geodetic2enu,aer2enu,aer2ecef,ecef2aer
from pymap3d.vincenty import vdist
from histutils.findnearest import findClosestAzel


def mergefov(w0:xarray.Dataset, w1:xarray.Dataset, projalt:float=110e3, method:str=None):
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
#%% find the ENU of narrow FOV pixels at 110km from narrow FOV
    w1 = pixelmask(w1, method)
    if method.lower() == 'mzslice':
        w0 = pixelmask(w0, method)
        azSlice0, elSlice0, rSlice0 = ecef2aer(w1.x2mz, w1.y2mz, w1.z2mz,
                                               w0.lat, w0.lon, w0.alt_m)
        azSlice1, elSlice1, rSlice1 = ecef2aer(w0.x2mz, w0.y2mz, w0.z2mz,
                                               w1.lat, w1.lon, w1.alt_m)
        # find image indices (mask) corresponding to slice az,el
        w0['rows'], w0['cols'] = findClosestAzel(w0['az'], w0['el'], azSlice0, elSlice0)
        w0.attrs['Brow'], w0.attrs['Bcol'] = findClosestAzel(w0['az'], w0['el'], w0.Baz, w0.Bel)
        
        w1['rows'], w1['cols'] = findClosestAzel(w1['az'], w1['el'], azSlice1, elSlice1)
        w1.attrs['Brow'], w1.attrs['Bcol'] = findClosestAzel(w1['az'], w1['el'], w1.Baz, w1.Bel)
    else:
        slantrange = projalt / np.sin(np.radians(np.ma.masked_invalid(w1['el'].where(w1['fovmask']))))    # csc(x) = 1/sin(x)
        assert (slantrange >= projalt).all(), 'slantrange must be >= projection altitude'
    
        e0, n0, u0 = aer2enu(w1['az'], w1['el'], slantrange)
    #%% find az,el to narrow FOV from ASI FOV
        az0,el0,_ = enu2aer(e0-e1, n0-n1, u0-u1)
        assert (el0 >= 0).all(), 'FOVs may not overlap, negative elevation from cam0 to cam1'
    #%% nearest neighbor brute force
        w0['rows'], w0['cols'] = findClosestAzel(w0['az'], w0['el'], az0, el0)

    return w0,w1


def pixelmask(data:xarray.Dataset, method:str) -> xarray.Dataset:
    """
    Use list because image may not be square

    returns mask of chosen pixels
    """
    if method is None or method == 'rect':  # outermost edge of image (trivial)
        mask = np.zeros(data['az'].shape, dtype=bool)
        mask[:, 0] = True; mask[0, :] = True
        mask[:,-1] = True; mask[-1,:] = True
    elif method=='perimeter': # perimeter for arbitrary shapes  e.g all-sky cameras
        mask = ndi.distance_transform_cdt(~np.isnan(data['az']), 'taxicab') == 1
    elif method.lower()=='mzslice':
        srpts = np.logspace(4.3, 6.9, 40)
        data.attrs['x2mz'], data.attrs['y2mz'], data.attrs['z2mz'] = aer2ecef(data.attrs['Baz'],data.attrs['Bel'], srpts,
                                                                              data.attrs['lat'],data.attrs['lon'],data.attrs['alt_m'])
        return data        
    else:
        raise ValueError(f'unknown mask {method}')
# %% sanity check
    if ~mask.any():
        raise ValueError('no FOV overlap found')


    data['fovmask'] = (('y','x'),mask)

    return data

