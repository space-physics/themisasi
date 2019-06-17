from dateutil.parser import parse
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import asyncio
import logging
import sys
import os
from aiohttp_requests import requests
from typing import Sequence, Union, Iterator, Dict

TIMEOUT = 600  # arbitrary, seconds

if sys.version_info < (3, 7):
    raise RuntimeError('Python >= 3.7 required')


async def urlretrieve(url: str, fn: Path, overwrite: bool = False):
    if not overwrite and fn.is_file() and fn.stat().st_size > 10000:
        print(f'SKIPPED {fn}')
        return
# %% download
    R = await requests.get(url, allow_redirects=True, timeout=TIMEOUT)

    if R.status != 200:
        logging.error(f'could not download {url}  {R.status}')
        return

    print(url)

    data = await R.read()

    with fn.open('wb') as f:
        f.write(data)


def download(treq: Sequence[Union[str, datetime]],
             site: Sequence[str], odir: Path,
             urls: Dict[str, str], overwrite: bool = False):
    """
    concurrent download video and calibration files

    Parameters
    ----------

    treq : datetime or list of datatime
        time request e.g. '2012-02-01T03' or a time range ['2012-02-01T03', '2012-02-01T05']
    site : str or list of str
        camera site e.g. gako, fykn
    odir : pathlib.Path
        output directory e.g. ~/data
    overwrite : bool
        overwrite existing files--normally wasteful of download space, unless you had a corrupted download.
    urls : dict of str
        stem of URLs to [web]site(s) hosting files
    """

# %% sanity checks
    odir = Path(odir).expanduser().resolve()
    odir.mkdir(parents=True, exist_ok=True)

    if isinstance(site, str):
        site = [site]

    if isinstance(treq, (str, datetime)):
        treq = [treq]

    start = parse(treq[0]) if isinstance(treq[0], str) else treq[0]
    if len(treq) == 2:
        end = parse(treq[1]) if isinstance(treq[1], str) else treq[1]
    else:
        end = start

    if end < start:
        raise ValueError('start time must be before end time!')
# %% start download
    if os.name == 'nt' and sys.version_info < (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # type: ignore

    asyncio.run(arbiter(site, start, end, odir, overwrite, urls))


async def arbiter(sites: Sequence[str],
                  start: datetime, end: datetime,
                  odir: Path, overwrite: bool,
                  urls: Dict[str, str]):
    """
    This starts len(sites) tasks concurrently.
    Thus if you only have one site, it only downloads one file at a time.

    A more elegant way is to setup a task pool.
    However normally we are downloading N sites across the same timespan,
    where N is typically in the 3..10 range or so.

    Parameters
    ----------
    sites : str or list of str
        sites to download video from
    start : datetime
        starting time
    end : datetime
        ending time
    odir : Path
        where to download data to
    overwrite : bool, optional
        overwrite existing data
    urls : dict of str
        sites hosting data


    Example of task pool:
    https://github.com/ec500-software-engineering/asyncio-subprocess-ffmpeg/blob/c82d3a243078d8e865740cd9c3328fe7fd6ea52e/asyncioffmpeg/ffplay.py#L45

    """

    futures = [_download_cal(site, odir, urls['cal_stem'], overwrite) for site in sites]

    await asyncio.gather(*futures)

    futures = [_download_video(site, odir, start, end, urls['video_stem'], overwrite) for site in sites]

    await asyncio.gather(*futures)


async def _download_video(site: str, odir: Path,
                          start: datetime, end: datetime,
                          url_stem: str, overwrite: bool):

    for url in _urlgen(site, start, end, url_stem):
        print('GEN: ', url)
        await urlretrieve(url, odir / url.split('/')[-1], overwrite)


def _urlgen(site: str, start: datetime, end: datetime, url_stem: str) -> Iterator[str]:

    for T in np.arange(start, end+timedelta(hours=1), timedelta(hours=1)):
        t = T.astype(datetime)
        fpath = (f'{url_stem}{site}/{t.year:4d}/{t.month:02d}/'
                 f'thg_l1_asf_{site}_{t.year:4d}{t.month:02d}{t.day:02d}{t.hour:02d}_v01.cdf')

        yield fpath


async def _download_cal(site: str, odir: Path, url_stem: str,
                        overwrite: bool = False):

    fpath = f"{url_stem}thg_l2_asc_{site}_19700101_v01.cdf"

    await urlretrieve(fpath,  odir / fpath.split('/')[-1], overwrite)
