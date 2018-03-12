from pathlib import Path
from numpy import flipud
import h5py
from scipy.io import readsav
try:
    from netCDF4 import Dataset
except ImportError:
    Dataset=None

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
            raise ImportError('you need netCDF4.    pip install netcdf4')
        with Dataset(str(fn),'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lla= {'lat':h['lla'][0], 'lon':h['lla'][1], 'alt_m':h['lla'][2]}
            x  = h['x'][:].astype(int)
            y  = flipud(h['y'][:]).astype(int)

    return az,el,lla,x,y
