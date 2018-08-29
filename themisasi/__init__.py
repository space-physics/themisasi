from dateutil.parser import parse
from datetime import datetime, timedelta
from pathlib import Path
import requests
import logging
import numpy as np
from typing import Sequence, Union
from .io import load, loadcal  # noqa: F401

URL = 'http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/'


def urlretrieve(url: str, fn: Path, overwrite: bool=False):
    if not overwrite and fn.is_file() and fn.stat().st_size > 10000:
        print(f'SKIPPED {fn}')
        return
# %% prepare to download
    R = requests.head(url, allow_redirects=True, timeout=10)
    if R.status_code != 200:
        logging.error(f'{url} not found. \n HTTP ERROR {R.status_code}')
        return
# %% download
    print(f'downloading {int(R.headers["Content-Length"])//1000000} MBytes:  {fn.name}')
    R = requests.get(url, allow_redirects=True, timeout=10)
    with fn.open('wb') as f:
        f.write(R.content)


def download(treq: Sequence[Union[str, datetime]], site: str, odir: Path, overwrite: bool=False, host: str=URL):
    """
    treq: time request e.g. '2012-02-01T03' or a time range ['2012-02-01T03', '2012-02-01T05']
    site: camera site e.g. gako, fykn
    odir: output directory e.g. ~/data
    overwrite: overwrite existing files--normally wasteful of download space, unless you had a corrupted download.
    host: website hosting files
    """
    if not host:
        raise ValueError(f'Must specify download host, e.g. {URL}')

# %% sanity checks
    odir = Path(odir).expanduser().resolve()
    if not odir.is_dir():
        raise FileNotFoundError(f'{odir} does not exist')

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
    for T in np.arange(start, end+timedelta(hours=1), timedelta(hours=1)):
        t = T.astype(datetime)
        fpath = (f'{host}{site}/{t.year:4d}/{t.month:02d}/'
                 f'thg_l1_asf_{site}_{t.year:4d}{t.month:02d}{t.day:02d}{t.hour:02d}_v01.cdf')

        urlretrieve(fpath, odir / fpath.split('/')[-1])
