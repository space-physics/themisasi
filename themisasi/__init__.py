from dateutil.parser import parse
from datetime import datetime
from pathlib import Path
import requests
import logging
from typing import List, Union


def urlretrieve(url: str, fn: Path, overwrite: bool=False):
    if not overwrite and fn.is_file() and fn.stat().st_size > 10000:
        print(f'SKIPPED {fn}')
        return

    with fn.open('wb') as f:

        R = requests.head(url, allow_redirects=True, timeout=10)
        if R.status_code != 200:
            logging.error(f'{url} not found. \n HTTP ERROR {R.status_code}')
            return

        print(f'downloading {int(R.headers["Content-Length"])//1000000} MBytes:  {fn.name}')

        R = requests.get(url, allow_redirects=True, timeout=10)

        f.write(R.content)


def download(treq: List[Union[str, datetime]], host: str, site: str, odir: Path, overwrite: bool=False):
    """
    startend: tuple of datetime
    year,month,day: integer
    hour, minute:  start,stop integer len == 2
    """
# %% sanity checks
    odir = Path(odir).expanduser().resolve()
    if not odir.is_dir():
        raise FileNotFoundError(f'{odir} does not exist')

    if isinstance(treq, (str, datetime)):
        treq = [treq]

    start = parse(treq[0]) if isinstance(treq[0], str) else treq[0]
    if len(treq) == 2:
        end = parse(treq[1]) if isinstance(treq[1], str) else treq[1]

    if end < start:
        raise ValueError('start time must be before end time!')
# %% start download
    fpath = (f'{host}{site}/{start.year:4d}/{start.month:2d}/'
             f'thg_l1_asf_{site}_{start.year:4d}{start.month:02d}{start.day:02d}{start.hour:02d}_v01.cdf')

    urlretrieve(fpath, odir / fpath.split('/')[-1])
