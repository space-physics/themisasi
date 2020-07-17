#!/usr/bin/env python
"""
Read THEMIS GBO ASI data
"""
import logging
import warnings
from pathlib import Path
from datetime import datetime, timedelta
import xarray
import typing as T
import numpy as np
from dateutil.parser import parse
import scipy.io

try:
    import cdflib

    Epoch = cdflib.cdfepoch()
    cdfread = cdflib.cdfread.CDF
except ImportError:
    Epoch = cdfread = None
try:
    import h5py
except ImportError:
    h5py = None
try:
    import netCDF4
except ImportError:
    netCDF4 = None


def load(
    path: Path, site: str = None, treq: T.List[datetime] = None, calfn: Path = None
) -> xarray.Dataset:
    """
    read THEMIS ASI camera data

    If treq is not specified, the whole file is loaded

    Parameters
    ----------
    path: pathlib.Path
        directory where Themis ASI data files are
    site: str, optional
        site code e.g. gako.  Only needed if "path" is a directory instead of a file
    treq: datetime.datetime or list of datetime.datetime, optional
        requested time to load
    calfn: pathlib.Path, optional
        path to calibration file (skymap)

    Returns
    -------
    data: xarray.Dataset
        Themis ASI data (image stack)
    """
    # %% time slice (assumes monotonically increasing time)
    if treq is not None:
        treq = _timereq(treq)

    imgs = _timeslice(path, site, treq)
    # %% optional load calibration (az, el)
    data = xarray.Dataset({"imgs": imgs})
    data.attrs = imgs.attrs

    cal = None
    if calfn:
        cal = loadcal(calfn, site, treq)
    else:
        try:
            cal = loadcal(path, site, treq)
        except FileNotFoundError:
            pass

    if cal is not None:
        if cal.site is not None and cal.site != imgs.site:
            raise ValueError(
                f"cal site {cal.site} and data site {imgs.site} do not match. Was wrong calibration file used?"
            )

        data = xarray.merge((data, cal))
        data.attrs = cal.attrs
        data.attrs.update(imgs.attrs)
        if data.caltime is not None:
            if (np.datetime64(data.caltime) >= data.time).any():
                raise ValueError(
                    "calibration is taken AFTER the images--may be incorrect lat/lon az/el plate scale"
                )

    return data


def filetimes(fn: Path) -> T.List[datetime]:
    """
    prints the times available in a THEMIS ASI CDF file

    Parameters
    ----------
    fn: pathlib.Path
        path to ASI data file

    Returns
    -------
    time: list of datetime.datetime
        times available in this CDF file
    """
    if not cdfread:
        raise ImportError("pip install cdflib")

    h = cdfread(fn)

    site = h.attget("Descriptor", 0)["Data"][:4].lower()

    return Epoch.to_datetime(h[f"thg_asf_{site}_epoch"][:])


def _timeslice(path: Path, site: str = None, treq: T.Sequence[datetime] = None) -> xarray.DataArray:
    """
    loads time slice of Themis ASI data

    Parameters
    ----------
    path: pathlib.Path
        directory where Themis asi data is
    site: str
        site code e.g. gako for Gakon
    treq: datetime.datetime or list of datetime.datetime
        requested time or min,max time range

    Results
    -------
    data: xarray.DataArray
        Themis ASI data
    """
    TIME_TOL = 1  # number of seconds to tolerate in time request offset
    # %% open CDF file handle (no close method)
    site, fn = _sitefn(path, site, treq)

    h = cdfread(fn)
    # %% load image times
    try:
        time = Epoch.to_datetime(h[f"thg_asf_{site}_epoch"][:], to_np=True)
    except (ValueError, KeyError):
        time = np.array(list(map(datetime.utcfromtimestamp, h[f"thg_asf_{site}_time"][:])))
    # %% time request handling
    if treq is None:
        i = slice(None)
    else:
        atreq = np.atleast_1d(treq)

        if atreq.size == 1:
            # Note: arbitrarily allowing up to 1 second time offset from request
            if all(atreq < (time - timedelta(seconds=TIME_TOL))) | all(
                atreq > time + timedelta(seconds=TIME_TOL)
            ):
                raise ValueError(f"requested time {atreq} outside {fn}")

            i = abs(time - atreq[0]).argmin()
        elif atreq.size == 2:  # start, end
            i = (time >= atreq[0]) & (time <= atreq[1])
        else:
            raise ValueError("for now, time req is single time or time range")

    imgs = h[f"thg_asf_{site}"][i]
    if imgs.ndim == 2:
        imgs = imgs[None, ...]

    time = time[i]
    if isinstance(time, datetime):
        time = [time]
    elif len(time) == 0:
        raise ValueError(f"no times were found with requested time bounds {treq}")

    return xarray.DataArray(
        imgs,
        coords={"time": time},
        dims=["time", "y", "x"],
        attrs={"filename": fn.name, "site": site},
    )


def _sitefn(path: Path, site: str = None, treq: T.Union[datetime, T.Sequence[datetime]] = None) -> T.Tuple[str, Path]:
    """
    gets site name and CDF key from filename

    Parameters
    ----------
    path: pathlib.Path
        directory or path to THemis ASI data file
    site: str
        site code e.g. gako for Gakona
    treq: datetime.datetime or list of datetime.datetime
        requested time or time range

    Returns
    -------
    site: str
        site code
    fn: pathlib.Path
        path to Themis ASI data file
    """

    path = Path(path).expanduser()

    if path.is_dir():
        if not isinstance(site, str):
            raise ValueError("Must specify filename OR path and site and time")

        # FIXME: assumes time bounds don't cross file boundaries
        if treq is None:
            raise ValueError("Must specify filename OR path and site and time")
        elif isinstance(treq, datetime):
            t0 = treq
        elif isinstance(treq[0], datetime) and len(treq) in (1, 2):
            t0 = treq[0]
        else:
            raise ValueError("Must specify filename OR path and site and time")

        fn = path / f"thg_l1_asf_{site}_{t0.year}{t0.month:02d}{t0.day:02d}{t0.hour:02d}_v01.cdf"
        if not fn.is_file():
            # try to use last time in file, if first time wasn't covered
            if isinstance(treq, datetime):
                raise FileNotFoundError(fn)

            t0 = treq[-1]

            fn = path / f"thg_l1_asf_{site}_{t0.year}{t0.month:02d}{t0.day:02d}{t0.hour:02d}_v01.cdf"

    elif path.is_file():
        fn = path

        h = cdfread(fn)
        if not site:
            site = h.attget("Descriptor", 0)["Data"][:4].lower()
        if site != h.attget("Descriptor", 0)["Data"][:4].lower():
            raise ValueError(f"{site} is not in {fn}")
    else:
        raise FileNotFoundError(path)

    return site, fn


def _timereq(treq: T.List[datetime]) -> T.List[datetime]:
    """
    parse time request
    """

    if isinstance(treq, datetime):
        pass
    elif isinstance(treq, str):
        treq = parse(treq)
    elif isinstance(treq[0], str):  # type: ignore
        treq = list(map(parse, treq))  # type: ignore
    elif isinstance(treq[0], datetime):  # type: ignore
        pass
    else:
        raise TypeError(treq)

    return treq


def _downsample(
    imgs: xarray.Dataset, az: np.ndarray, el: np.ndarray, x: np.ndarray, y: np.ndarray
) -> xarray.Dataset:
    """
    downsamples cal data to match image data

    because of the discontinuous nature of the calibration data, typical resampling is not valid.
    Figured better to add a little error with plain decimation rather than enormous error with invalid technique.
    """
    if az.shape == imgs.shape[1:]:
        return az, el, x, y

    downscale = (az.shape[0] // imgs.shape[1], az.shape[1] // imgs.shape[2])

    logging.warning(
        f"downsizing calibration az/el data by factors of {downscale} to match image data"
    )

    az = az[:: downscale[0], :: downscale[1]]
    el = el[:: downscale[0], :: downscale[1]]
    x = np.arange(az.shape[1])
    y = np.arange(az.shape[0])

    return az, el, x, y


def loadcal_file(fn: Path) -> xarray.Dataset:
    """
    reads data mapping themis gbo asi pixels to azimuth,elevation
    calibration data url is
    http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/

    Parameters
    ----------
    fn: pathlib.Path
        path to calibration file

    Returns
    -------
    cal: xarray.Dataset
        calibration data
    """
    site = None
    time = None
    fn = Path(fn).expanduser()
    if not fn.is_file():
        raise FileNotFoundError(fn)

    if fn.suffix == ".cdf":
        site = fn.name.split("_")[3]
        if cdfread is None:
            raise ImportError("pip install cdflib")

        h = cdfread(fn)
        az = h[f"thg_asf_{site}_azim"][0]
        el = h[f"thg_asf_{site}_elev"][0]
        lat = h[f"thg_asc_{site}_glat"]
        lon = (h[f"thg_asc_{site}_glon"] + 180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h[f"thg_asc_{site}_alti"]
        x = y = h[f"thg_asf_{site}_c256"]
        time = datetime.utcfromtimestamp(h[f"thg_asf_{site}_time"][-1])
    elif fn.suffix == ".sav":
        site = fn.name.split("_")[2]
        # THEMIS SAV calibration files written with glitch from bug in IDL
        warnings.simplefilter("ignore", UserWarning)
        h = scipy.io.readsav(fn, python_dict=True, verbose=False)
        warnings.resetwarnings()

        az = h["skymap"]["full_azimuth"][0]
        el = h["skymap"]["full_elevation"][0]
        lat = h["skymap"]["site_map_latitude"].item()
        lon = (h["skymap"]["site_map_longitude"].item() + 180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h["skymap"]["site_map_altitude"].item()
        x = h["skymap"]["full_column"][0][0, :]
        y = h["skymap"]["full_row"][0][:, 0]
        try:
            tstr = h["skymap"]["generation_info"][0][0][2]
            time = datetime(int(tstr[:4]), int(tstr[4:6]), int(tstr[6:8]), int(tstr[8:10]))
        except (KeyError, ValueError):
            if h["skymap"]["site_unix_time"] > 0:
                tutc = h["skymap"]["site_unix_time"]
            elif h["skymap"]["imager_unix_time"] > 0:
                tutc = h["skymap"]["imager_unix_time"]
            else:
                tutc = None

            if tutc is not None:
                time = datetime.utcfromtimestamp(tutc)
            else:  # last resort
                time = datetime(int(fn.name[19:23]), int(fn.name[23:25]), int(fn.name[25:27]))

    elif fn.suffix == ".h5":
        if h5py is None:
            raise ImportError("pip install h5py")

        with h5py.File(fn, "r") as h:
            az = h["az"][:]
            el = h["el"][:]
            lat = h["lla"][0]
            lon = h["lla"][1]
            alt_m = h["lla"][2]
            x = h["x"][0, :]
            y = h["y"][:, 0]
    elif fn.suffix == ".nc":
        if netCDF4.Dataset is None:
            raise ImportError("pip install netCDF4")

        with netCDF4.Dataset(fn, "r") as h:
            az = h["az"][:]
            el = h["el"][:]
            lat = h["lla"][0]
            lon = h["lla"][1]
            alt_m = h["lla"][2]
            x = h["x"][0, :].astype(int)
            y = np.flipud(h["y"][:, 0]).astype(int)
    else:
        raise ValueError(f"{fn} calibration file format is not known to this program.")

    cal = xarray.Dataset(
        {"az": (("y", "x"), az), "el": (("y", "x"), el)},
        coords={"y": y, "x": x},
        attrs={
            "lat": lat,
            "lon": lon,
            "alt_m": alt_m,
            "site": site,
            "calfilename": fn.name,
            "caltime": time,
        },
    )

    return cal


def loadcal(path: Path, site: str = None, time: T.Sequence[datetime] = None) -> xarray.Dataset:
    """
    load calibration skymap file

    Parameters
    ----------
    path: pathlib.Path
        directory or path to calibration file
    site: str
        site code e.g. gako
    time: datetime.datetime or list of datetime.datetime
        time requested

    Returns
    -------
    cal: xarray.Dataset
        calibration data
    """
    path = Path(path).expanduser()

    if path.is_file():
        if site is None or time is None:
            try:
                return loadcal_file(path)
            except (KeyError, ValueError):
                return None
        else:
            path = path.parent

    assert isinstance(site, str)
    fn = _findcal(path, site, time)

    return loadcal_file(fn)


def _findcal(path: Path, site: str, time: T.Sequence[datetime]) -> Path:
    """
    attempt to find nearest previous time calibration file
    """

    if not path.is_dir():
        raise FileNotFoundError(str(path))

    if not isinstance(site, str) or len(site) != 4:
        raise ValueError(f"site code is four characters e.g. fykn.  You gave:   {site}")

    if isinstance(time, str):
        time = parse(time)

    if isinstance(time, (list, tuple, np.ndarray)):
        time = time[0]  # assume first time is earliest

    if not isinstance(time, datetime):
        raise TypeError(f"must specify single datetime, you gave:  {time}")
    # %% CDF .cdf
    fcdf = list(path.glob(f"thg_l2_asc_{site}_*.cdf"))
    cdates = [loadcal(fn).caltime for fn in fcdf]

    datecdf = None
    if cdates:
        for _i, date in enumerate(cdates):
            if date < time:
                break
        if date < time:
            datecdf = date
            icdf = len(cdates) - (_i + 1)
    # %% IDL .sav
    fsav = list(path.glob(f"themis_skymap_{site}_*.sav"))
    sdates = [loadcal(fn).caltime for fn in fsav]

    datesav = None
    if sdates:
        for _i, date in enumerate(sdates):
            if date < time:
                break
        if date < time:
            datesav = date
            isav = len(sdates) - (_i + 1)

    # %% get result
    if not sdates and not cdates:
        raise FileNotFoundError(f"could not find cal file for {site} {time}  in {path}")
    elif datecdf is None:
        return fsav[isav]
    elif datesav is None:
        return fcdf[icdf]
    # tiebreaker
    diff = [abs(datecdf - time), abs(datesav - time)]
    idff = diff.index(min(diff))

    if idff == 0:
        return fcdf[icdf]
    else:
        return fsav[isav]
