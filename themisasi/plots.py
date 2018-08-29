from pathlib import Path
import xarray
import numpy as np
from datetime import datetime
from matplotlib.pyplot import figure, draw, pause
from matplotlib.colors import LogNorm
import pymap3d as pm


def jointazel(cam: xarray.Dataset, ofn: Path=None, ttxt: str=''):

    fg, axs = plotazel(cam, ttxt)
# %% plot line from other camera to magnetic zenith
    overlayrowcol(axs[0], cam.rows, cam.cols, 'g')
    overlayrowcol(axs[1], cam.rows, cam.cols, 'g')
# %% plot plane including this camera and line to magnetic zenith from other camera
    try:
        axs[0] = overlayrowcol(axs[0], cam.cutrow, cam.cutcol, 'r', '1-D cut')
        axs[1] = overlayrowcol(axs[1], cam.cutrow, cam.cutcol, 'r', '1-D cut')
    except AttributeError:
        pass  # this was not a 1-D plane case

    if ofn:
        ofn = Path(ofn).expanduser()
        print('saving', ofn)
        fg.savefig(ofn, bbox_inches='tight', dpi=100)

    if 'Baz' in cam.attrs:
        axs[0].scatter(cam.Bcol, cam.Brow, 250, 'red', '*', label='Mag. Zen.')
        axs[1].scatter(cam.Bcol, cam.Brow, 250, 'red', '*', label='Mag. Zen.')

    for a in axs:
        a.legend()


def plotazel(data: xarray.Dataset, ttxt: str=''):

    if 'az' not in data or 'el' not in data:
        return

    fg = figure(figsize=(12, 6))
    ax = fg.subplots(1, 2, sharey=True)

    ttxt = f'{data.filename} {ttxt}'
    if data.caltime is not None:
        ttxt += f'{data.caltime}'

    fg.suptitle(ttxt)

    c = ax[0].contour(data['az'].x, data['az'].y, data['az'])
    ax[0].clabel(c, fmt='%0.1f')
    ax[0].set_title('azimuth')
    ax[0].set_xlabel('x-pixels')
    ax[0].set_ylabel('y-pixels')

    c = ax[1].contour(data['el'].x, data['el'].y, data['el'])
    ax[1].clabel(c, fmt='%0.1f')
    ax[1].set_title('elevation')
    ax[1].set_xlabel('x-pixels')

    return fg, ax


def plottimeseries(data: np.ndarray, time: datetime, ttxt: str=''):

    assert data.ndim == 2

    ax = figure().gca()

    ax.plot(time, data)
    ax.set_xlabel('time')
    ax.set_ylabel('brightness [data numbers]')
    ax.set_title(ttxt)


def overlayrowcol(ax, rows, cols, color: str=None, label: str=None):
    """
    plot FOV outline onto image via the existing axis "ax"

    inputs:
    ax: existing plot axis to overlay lines outlining FOV
    rows,cols: indices to plot
    """
    if rows is None or cols is None:
        return

    if len(rows) == 1 or isinstance(rows, (np.ndarray, xarray.DataArray)) and rows.ndim == 1:
        ax.scatter(cols, rows, color=color, alpha=0.5, marker='.', label=label)
    else:
        raise ValueError('unknonn row/col layout, was expecting 1-D')

    return ax
# %%


def plotasi(data: xarray.Dataset, ofn: Path=None):
    """
    rows,cols expect lines to be along rows Nlines x len(line)
    list of 1-D arrays or 2-D array
    """

    if data['imgs'].shape[0] == 0:
        return

    if ofn:
        ofn = Path(ofn).expanduser()
        odir = ofn.parent

    fg = figure()
    ax = fg.gca()

    hi = ax.imshow(data['imgs'][0], cmap='gray', origin='lower',
                   norm=LogNorm(), interpolation='none')  # priming
    ttxt = f'Themis ASI {data.site}\n'  # FOV vs. HST0,HST1: green,red '
    ht = ax.set_title(ttxt, color='g')
    ax.set_xlabel('x-pixels')
    ax.set_ylabel('y-pixels')
    ax.autoscale(True, tight=True)
    ax.grid(False)
# %% plot narrow FOV outline
    if 'imgs2' in data:
        overlayrowcol(ax, data.rows, data.cols)
# %% play video
    try:
        for im in data['imgs']:
            ts = str(im.time.astype('datetime64[us]').astype(datetime))
            hi.set_data(im)
            ht.set_text(ttxt + ts)
            draw()
            pause(0.01)
            if ofn:
                fn = odir / (ofn.stem + ts + ofn.suffix)
                print('saving', fn, end='\r')
                fg.savefig(fn, bbox_inches='tight', facecolor='k')
    except KeyboardInterrupt:
        return


def asi_projection(dat: xarray.Dataset, alt_km: float=None, ofn: Path=None):
    """
    plots ASI projected to altitude
    """
    if alt_km is None:
        plotasi(dat, ofn)
        return

    if dat['imgs'].shape[0] == 0:
        return

    if ofn:
        ofn = Path(ofn).expanduser()
        odir = ofn.parent

    srange = alt_km / np.sin(np.radians(dat.el.values))
    lat, lon, alt = pm.aer2geodetic(dat.az.values, dat.el.values, srange,
                                    dat.lat, dat.lon, dat.alt_km)

    fg = figure()
    ax = fg.gca()

    hi = pcolormesh_nan(lon, lat, dat['imgs'][0], cmap='gray', axis=ax)  # priming

    ttxt = f'Themis ASI {dat.site}  projected to altitude {alt_km} km\n'  # FOV vs. HST0,HST1: green,red '
    ht = ax.set_title(ttxt, color='g')
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    ax.autoscale(True, tight=True)
    ax.grid(False)
# %% plot narrow FOV outline
    if 'imgs2' in dat:
        overlayrowcol(ax, dat.rows, dat.cols)
# %% play video
    try:
        for im in dat['imgs']:
            ts = im.time.values.astype(str)[:-6]
            hi.set_data(im)
            ht.set_text(ttxt + ts)
            draw()
            pause(0.01)
            if ofn:
                fn = odir / (ofn.stem + ts + ofn.suffix)
                print('saving', fn, end='\r')
                fg.savefig(fn, bbox_inches='tight', facecolor='k')
    except KeyboardInterrupt:
        return


def asi_radec(dat: xarray.Dataset, ofn: Path=None):
    """
    plots ASI projected to altitude
    """

    if dat['imgs'].shape[0] == 0:
        return

    if ofn:
        ofn = Path(ofn).expanduser()

    az = dat.az.values
    el = dat.el.values
    az.setflags(write=True)
    el.setflags(write=True)

    bad = el < 10  # low to horizon, calibration is very bad
    az[bad] = np.nan
    el[bad] = np.nan

    ra, dec = pm.azel2radec(az, el, dat.lat, dat.lon, dat.time)

    fg = figure()
    ax = fg.gca()

    pcolormesh_nan(ra, dec, dat['imgs'].values[0], cmap='gray', axis=ax)  # priming

    ttxt = f'Themis ASI {dat.site}  \n'
    ax.set_title(ttxt, color='g')
    ax.set_xlabel('right ascension [deg]')
    ax.set_ylabel('declination [deg]')
    ax.autoscale(True, tight=True)
    ax.grid(False)


def pcolormesh_nan(x: np.ndarray, y: np.ndarray, c: np.ndarray, cmap=None, axis=None):
    """handles NaN in x and y by smearing last valid value in column or row out,
    which doesn't affect plot because "c" will be masked too
    """

    mask = np.isfinite(x) & np.isfinite(y)
    top = None

    for i, m in enumerate(mask):
        good = m.nonzero()[0]

        if good.size == 0:
            continue
        elif top is None:
            top = i
        else:
            bottom = i

        x[i, good[-1]:] = x[i, good[-1]]
        y[i, good[-1]:] = y[i, good[-1]]

        x[i, :good[0]] = x[i, good[0]]
        y[i, :good[0]] = y[i, good[0]]

    x[:top, :] = np.nanmean(x[top, :])
    y[:top, :] = np.nanmean(y[top, :])

    x[bottom:, :] = np.nanmean(x[bottom, :])
    y[bottom:, :] = np.nanmean(y[bottom, :])

    if axis is None:
        axis = figure().gca()

    return axis.pcolormesh(x, y, np.ma.masked_where(~mask, c), cmap=cmap)
