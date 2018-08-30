#!/usr/bin/env python
"""
Multi-camera view
GAKO: http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/gako/2008/03/
+ PFRR
"""
import themisasi as ta
import themisasi.plots as tap
from pathlib import Path
from matplotlib.pyplot import show
try:
    import seaborn as sns
    sns.set_context('talk')
except ImportError:
    pass

# %% user parameters
datadir = Path('~/data/themis').expanduser()
site = 'gako'
asifn = ('thg_l1_asf_gako_2008032607_v01.cdf',
         'thg_l1_asf_gako_2008032608_v01.cdf')
treq = [('2008-03-26T07:34', '2008-03-26T07:38'),  # Slide 9
        ('2008-03-26T07:46', '2008-03-26T07:50'),  # Slide 15
        ('2008-03-26T08:16', '2008-03-26T08:20'),  # Slide 30
        ]
odir = None

asical = datadir / 'themis_skymap_gako_20070401.sav'
# %% load data, with calibration az/el
data0 = ta.load(datadir / asifn[0], treq=treq[0], calfn=asical)
data1 = ta.load(datadir / asifn[0], treq=treq[1], calfn=asical)
data2 = ta.load(datadir / asifn[1], treq=treq[2], calfn=asical)
# %% plot
tap.plotasi(data0)
tap.plotasi(data1)
tap.plotasi(data2)

tap.plotazel(data0)

show()
