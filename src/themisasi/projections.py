import xarray
from pathlib import Path
import pymap3d as pm
import logging
import numpy as np
from matplotlib.pyplot import figure, draw, pause
from .plots import pcolormesh_nan, overlayrowcol


def asi_projection(
    dat: xarray.Dataset, projalt_m: float = None, min_el: float = 10.0, ofn: Path = None
):
    """
    plots ASI projected to altitude

    * dat: Xarray containing image stack and metadata (az, el, lat, lon)
    * projalt_m: projection altitude in meters
    * min_el: minimum elevation angle (degrees). Data near the horizon is poorly calibrated (large angular error).
    * ofn: filename to write of plot (optional)
    """
    if projalt_m is None:
        logging.error("projection altitude must be specified")
        return

    if dat["imgs"].shape[0] == 0:
        return

    if ofn:
        ofn = Path(ofn).expanduser()
        odir = ofn.parent

    # %% censor pixels near the horizon with large calibration error do to poor skymap fits
    badpix = dat["el"] < min_el
    az = dat["az"].values
    el = dat["el"].values
    az[badpix] = np.nan
    el[badpix] = np.nan
    # %% coordinate transformation, let us know if error occurs
    slant_range = projalt_m / np.sin(np.radians(el))

    lat, lon, alt = pm.aer2geodetic(
        az, el, slant_range, dat.lat.item(), dat.lon.item(), dat.alt_m.item()
    )
    # %% plots
    fg = figure()
    ax = fg.gca()

    hi = pcolormesh_nan(lon, lat, dat["imgs"][0], cmap="gray", axis=ax)  # priming

    ttxt = f"Themis ASI {dat.site}  projected to altitude {projalt_m/1e3} km\n"  # FOV vs. HST0,HST1: green,red '
    ht = ax.set_title(ttxt, color="g")
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.autoscale(True, tight=True)
    ax.grid(False)
    # %% plot narrow FOV outline
    if "imgs2" in dat:
        overlayrowcol(ax, dat.rows, dat.cols)
    # %% play video
    try:
        for im in dat["imgs"]:
            ts = im.time.values.astype(str)[:-6]
            hi.set_array(im.values.ravel())  # for pcolormesh
            ht.set_text(ttxt + ts)
            draw()
            pause(0.01)
            if ofn:
                fn = odir / (ofn.stem + ts + ofn.suffix)
                print("saving", fn, end="\r")
                fg.savefig(fn, bbox_inches="tight", facecolor="k")
    except KeyboardInterrupt:
        return


def asi_radec(dat: xarray.Dataset, min_el: float = 10.0, ofn: Path = None):
    """
    plots ASI projected to altitude

    * min_el: minimum elevation angle (degrees). Data near the horizon is poorly calibrated (large angular error).
    * ofn: filename to write of plot (optional)
    """

    if dat["imgs"].shape[0] == 0:
        return

    if ofn:
        ofn = Path(ofn).expanduser()

    az = dat.az.values
    el = dat.el.values
    az.setflags(write=True)
    el.setflags(write=True)

    bad = el < min_el  # low to horizon, calibration is very bad
    az[bad] = np.nan
    el[bad] = np.nan

    ra, dec = pm.azel2radec(az, el, dat.lat, dat.lon, dat.time)

    fg = figure()
    ax = fg.gca()

    pcolormesh_nan(ra, dec, dat["imgs"].values[0], cmap="gray", axis=ax)  # priming

    ttxt = f"Themis ASI {dat.site}  \n"
    ax.set_title(ttxt, color="g")
    ax.set_xlabel("right ascension [deg]")
    ax.set_ylabel("declination [deg]")
    ax.autoscale(True, tight=True)
    ax.grid(False)
