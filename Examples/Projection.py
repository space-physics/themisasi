#!/usr/bin/env python
"""
example of image projection to an altitude.
This assumes all the brightness comes from a thin layer at that altitude, which
is a common first-order approximation made in multi-instrument studies, for example using
auroral video with GNSS TEC measurements.
"""

from pathlib import Path

import themisasi as ta
import themisasi.download as tw
import themisasi.projections as tap

VIDEO_BASE = "https://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/"
CAL_BASE = "https://themis.ssl.berkeley.edu/data/themis/thg/l2/asi/cal/"
urls = {"video_stem": VIDEO_BASE, "cal_stem": CAL_BASE}


datadir = Path("~/data/2016-11-29").expanduser()

time_query = "2016-11-29T12"

tw.download(time_query, "mcgr", datadir, urls=urls)

dat = ta.load(datadir, site="mcgr", treq=time_query)

tap.asi_projection(dat, 110e3)
