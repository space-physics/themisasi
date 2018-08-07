import logging
import xarray
import numpy as np
from typing import Tuple
from pymap3d.haversine import anglesep
import pymap3d as pm
from pymap3d.vincenty import vdist
import histutils.findnearest as fnd
try:
    import scipy.ndimage as ndi
except ImportError:
    ndi = None


def getimgind(imgs: xarray.Dataset, lla: np.ndarray,
              az: np.ndarray, el: np.ndarray) -> np.ndarray:
    """ find pixels in images according to lat,lon,alt or az,el spec"""
    if lla is not None:
        lla = np.atleast_2d(lla)
        assert lla.ndim == 2
        assert lla.shape[1] == 3
        N = lla.shape[0]
    elif az is not None and el is not None:
        az = np.atleast_1d(az)
        el = np.atleast_1d(el)
        assert az.ndim == 1 and el.ndim == 1
        N = az.size
    else:
        raise ValueError('must specify LLA or az/el')
# %% work
    ind = np.empty((N, 2), dtype=int)

    if lla is not None:
        az, el, _ = pm.geodetic2aer(lla[:, 0], lla[:, 1], lla[:, 2]*1000,
                                    imgs.lat, imgs.lon, imgs.alt_m)

    for i, (a, e) in enumerate(zip(az, el)):
        ind[i, :] = fnd.findClosestAzel(imgs.az, imgs.el, a, e)

    ind = np.unique(ind, axis=0)

    assert ind.ndim == 2
    assert ind.shape[1] == 2  # row, column

    return ind


def projected_coord(imgs: xarray.Dataset, ind: np.ndarray, lla: Tuple[float, float, float]):
    az = imgs.az[ind[:, 0], ind[:, 1]].values.squeeze()
    el = imgs.el[ind[:, 0], ind[:, 1]].values.squeeze()

    alt_m = lla[2]*1000 if lla is not None else 100e3

    plat, plon, palt_m = pm.aer2geodetic(az, el, alt_m / np.sin(np.radians(el)),
                                         imgs.lat, imgs.lon, imgs.alt_m)

    return az, el, plat, plon, palt_m


def line2plane(cam: xarray.Dataset) -> xarray.Dataset:
    """
    previously, you find the row, col pixels along the line from the other camera to magnetic zenith.
    In this function, you find the indices of the plane passing through that line and both cameras.

    Inputs:
    -------
    row: row indices of line
    col: column indices of line
    nPlane: number of samples (pixels) to take for plane.
      If the plane is horizontal in the images, it would be approximately the number of x-pixels.
      If diagonal, it would be about sqrt(2)*Nx.
      If less, the image is sampled more sparsely, which is in effect recducing the resolution of the image.
      This parameter is not critical.
    """
# %% linear regression
    polycoeff = np.polyfit(cam['cols'], cam['rows'], deg=3, full=False)
# %% columns (x)  to cut from picture (have to pick either rows or cols, arbitrarily I use cols)
    # NOT range, NEED dtype= for arange api

# %% rows (y) to cut from picture
    cam['cutrow'] = np.rint(np.polyval(polycoeff, cam['cutcol'])).astype(int)
    assert (cam['cutrow'] >= 0).all() and (cam['cutrow'] < cam.y.size).all(
    ), 'impossible least squares fit for 1-D cut\n is your video orientation correct? are you outside the FOV?'

    # DONT DO THIS: cutrow.clip(0,self.supery,cutrow)
# %% angle from magnetic zenith corresponding to those pixels
    anglesep_deg = anglesep(cam.Bel, cam.Baz,
                            # NEED .values or you'll get 2-D instead of 1-D!
                            cam.el.values[cam.cutrow, cam.cutcol],
                            cam.az.values[cam.cutrow, cam.cutcol])

    if cam.verbose:
        from maatplotlib.pyplot import figure
        ax = figure().gca()
        ax.plot(cam.cutcol, anglesep_deg, label='angle_sep from MZ')
        ax.plot(cam.cutcol, cam.el.values[cam.cutrow,
                                          cam.cutcol], label='elevation angle [deg]')
        ax.legend()

    assert anglesep_deg.ndim == 1
    if not np.isfinite(anglesep_deg).all():
        logging.error(f'did you pick areas outside the {cam.filename} FOV?')
# %% assemble angular distances from magnetic zenith--these are used in the tomography algorithm
    cam['angle_deg'], cam['angleMagzenind'] = sky2beam(
        anglesep_deg, cam.cutcol.size)

    return cam


def sky2beam(anglesep_deg, Ncol: int):
    angle_deg = np.empty(Ncol, float)
    # whether minimum angle distance from MZ is slightly positive or slightly negative, this should be OK
    MagZenInd = anglesep_deg.argmin()

    angle_deg[MagZenInd:] = 90. + anglesep_deg[MagZenInd:]
    angle_deg[:MagZenInd] = 90. - anglesep_deg[:MagZenInd]
# %% LSQ
    col = np.arange(Ncol, dtype=int)
    polycoeff = np.polyfit(col, angle_deg, deg=1, full=False)

    return np.polyval(polycoeff, col), MagZenInd


def mergefov(w0: xarray.Dataset, w1: xarray.Dataset, projalt: float=110e3, method: str=None):
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
    if projalt < 1e3:
        logging.warning(
            f'this function expects meters, you picked projection altitude {projalt/1e3} km')

# %% print distance from wide camera to narrow camera (just for information)
    print(
        f"intercamera distance with {w0.site}:  {vdist(w0.lat,w0.lon, w1.lat,w1.lon)[0]/1e3:.1f} kilometers")
# %% ENU projection from cam0 to cam1
    e1, n1, u1 = pm.geodetic2enu(w1.lat, w1.lon, w1.alt_m,
                                 w0.lat, w0.lon, w0.alt_m)
# %% find the ENU of narrow FOV pixels at 110km from narrow FOV
    w1 = pixelmask(w1, method)
    if method is not None and method.lower() == 'mzslice':
        w0 = pixelmask(w0, method)
        azSlice0, elSlice0, rSlice0 = pm.ecef2aer(w1.x2mz, w1.y2mz, w1.z2mz,
                                                  w0.lat, w0.lon, w0.alt_m)
        azSlice1, elSlice1, rSlice1 = pm.ecef2aer(w0.x2mz, w0.y2mz, w0.z2mz,
                                                  w1.lat, w1.lon, w1.alt_m)
        # find image indices (mask) corresponding to slice az,el
        w0['rows'], w0['cols'] = fnd.findClosestAzel(w0['az'].where(w0['fovmask']),
                                                     w0['el'].where(w0['fovmask']),
                                                     azSlice0, elSlice0)
        w0.attrs['Brow'], w0.attrs['Bcol'] = fnd.findClosestAzel(
            w0['az'], w0['el'], w0.Baz, w0.Bel)

        w1['rows'], w1['cols'] = fnd.findClosestAzel(w1['az'].where(w1['fovmask']),
                                                     w1['el'].where(w1['fovmask']),
                                                     azSlice1, elSlice1)
        w1.attrs['Brow'], w1.attrs['Bcol'] = fnd.findClosestAzel(
            w1['az'], w1['el'], w1.Baz, w1.Bel)
    else:
        # csc(x) = 1/sin(x)
        slantrange = projalt / \
            np.sin(np.radians(np.ma.masked_invalid(
                w1['el'].where(w1['fovmask']))))
        assert (slantrange >= projalt).all(
        ), 'slantrange must be >= projection altitude'

        e0, n0, u0 = pm.aer2enu(w1['az'], w1['el'], slantrange)
    # %% find az,el to narrow FOV from ASI FOV
        az0, el0, _ = pm.enu2aer(e0 - e1, n0 - n1, u0 - u1)
        assert (el0 >= 0).all(
        ), 'FOVs may not overlap, negative elevation from cam0 to cam1'
    # %% nearest neighbor brute force
        w0['rows'], w0['cols'] = fnd.findClosestAzel(w0['az'], w0['el'], az0, el0)

    return w0, w1


def pixelmask(data: xarray.Dataset, method: str=None) -> xarray.Dataset:
    """
    Use list because image may not be square

    returns mask of chosen pixels
    """
    if method is None or method == 'rect':  # outermost edge of image (trivial)
        mask = np.zeros(data['az'].shape, dtype=bool)
        mask[:, 0] = True
        mask[0, :] = True
        mask[:, -1] = True
        mask[-1, :] = True
    elif method == 'perimeter':  # perimeter for arbitrary shapes  e.g all-sky cameras
        if ndi is None:
            raise ImportError('pip install scipy')

        mask = ndi.distance_transform_cdt(~np.isnan(data['az']), 'taxicab') == 1
    elif method.lower() == 'mzslice':
        """
        Assuming the imagers are all-sky, we arbitrarily discard pixels of low elevation as distortion is high low to horizon.
        """
        MIN_EL = 5  # degrees, arbitrary
        if data.srpts is None:
            return ValueError('must include slant range points')

        mask = np.zeros(data['az'].shape, dtype=bool)
        mask[data['el'] >= MIN_EL] = True

        data['fovmask'] = (('y', 'x'), mask)

        data.attrs['x2mz'], data.attrs['y2mz'], data.attrs['z2mz'] = pm.aer2ecef(data.attrs['Baz'], data.attrs['Bel'],
                                                                                 data.srpts,
                                                                                 data.attrs['lat'], data.attrs['lon'],
                                                                                 data.attrs['alt_m'])
        return data
    else:
        raise ValueError(f'unknown mask {method}')
# %% sanity check
    if ~mask.any():
        raise ValueError('no FOV overlap found')

    data['fovmask'] = (('y', 'x'), mask)

    return data
