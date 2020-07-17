from dateutil.parser import parse
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import asyncio
import logging
import sys
import os
import argparse
import requests
import typing as T

TIMEOUT = 600  # arbitrary, seconds
VIDEO_BASE = "http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/"
CAL_BASE = "http://themis.ssl.berkeley.edu/data/themis/thg/l2/asi/cal/"


def cli():
    p = argparse.ArgumentParser()
    p.add_argument(
        "startend", help="start/end times UTC e.g. 2012-11-03T06:23 2012-11-03T06:24", nargs="+"
    )
    p.add_argument("odir", help="directory to write downloaded CDF to")
    p.add_argument("-s", "--site", help="fykn gako etc.", nargs="+")
    p.add_argument("-overwrite", help="overwrite existing files", action="store_true")
    p.add_argument("-vh", help="Stem of URL for Video data", default=VIDEO_BASE)
    p.add_argument("-ch", help="Stem of URL for calibration data", default=CAL_BASE)

    P = p.parse_args()

    urls = {"video_stem": P.vh, "cal_stem": P.ch}

    download(P.startend, P.site, P.odir, P.overwrite, urls)


async def urlretrieve(url: str, fn: Path, overwrite: bool = False):
    if not overwrite and fn.is_file() and fn.stat().st_size > 10000:
        print(f"SKIPPED {fn}")
        return
    # %% download
    R = requests.get(url, allow_redirects=True, timeout=TIMEOUT)

    if R.status_code != 200:
        logging.error(f"could not download {url}  {R.status_code}")
        return

    print(url)

    fn.write_bytes(R.content)


def download(
    treq: T.Sequence[T.Union[str, datetime]],
    site: T.Sequence[str],
    odir: Path,
    urls: T.Dict[str, str],
    overwrite: bool = False,
):
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
        raise ValueError("start time must be before end time!")
    # %% start download
    if os.name == "nt" and sys.version_info < (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # type: ignore

    asyncio.run(arbiter(site, start, end, odir, overwrite, urls))


async def arbiter(
    sites: T.Sequence[str],
    start: datetime,
    end: datetime,
    odir: Path,
    overwrite: bool,
    urls: T.Dict[str, str],
):
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
    """

    futures = [_download_cal(site, odir, urls["cal_stem"], overwrite) for site in sites]

    await asyncio.gather(*futures)

    futures = [
        _download_video(site, odir, start, end, urls["video_stem"], overwrite) for site in sites
    ]

    await asyncio.gather(*futures)


async def _download_video(
    site: str, odir: Path, start: datetime, end: datetime, url_stem: str, overwrite: bool
):

    for url in _urlgen(site, start, end, url_stem):
        print("GEN: ", url)
        await urlretrieve(url, odir / url.split("/")[-1], overwrite)


def _urlgen(site: str, start: datetime, end: datetime, url_stem: str) -> T.Iterator[str]:

    for dt64 in np.arange(start, end + timedelta(hours=1), timedelta(hours=1)):
        t = dt64.astype(datetime)
        fpath = (
            f"{url_stem}{site}/{t.year:4d}/{t.month:02d}/"
            f"thg_l1_asf_{site}_{t.year:4d}{t.month:02d}{t.day:02d}{t.hour:02d}_v01.cdf"
        )

        yield fpath


async def _download_cal(site: str, odir: Path, url_stem: str, overwrite: bool = False):

    fpath = f"{url_stem}thg_l2_asc_{site}_19700101_v01.cdf"

    await urlretrieve(fpath, odir / fpath.split("/")[-1], overwrite)
