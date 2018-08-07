#!/usr/bin/env python
"""
paint HiST field of view onto Themis

"""
from datetime import datetime
from matplotlib.pyplot import show
from themisasi import altfiducial
from themisasi.plots import plotthemis
try:
    import seaborn as sns
    sns.set_context('talk')
except ImportError:
    pass


sitereq = 'whit'  # 'fykn' 'gako' 'mcgr'
# for this date, kian and whit are binned 32x32, we'd need to figure out the non-trivial binning to use them.
# kian and whit are far away, so this is a low priority.

# treq = (datetime(2013,4,14,8,30),datetime(2013,4,14,8,32)) #when big auroral hook  form for orientation happens
treq = (datetime(2013, 4, 14, 8, 53), datetime(
    2013, 4, 14, 8, 56))  # HIST event
odir = None

moviefn = f'THEMIS/{sitereq}_hst0,1_{treq[0].strftime("%Y-%m-%dT%H%M")}.mkv'
# %%

if sitereq == 'fykn':
    asifn = 'THEMIS/thg_l1_asf_fykn_2013041408_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_fykn_20110305-+_vXX.sav'
elif sitereq == 'gako':
    asifn = 'THEMIS/thg_l1_asf_gako_2013041408_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_gako_20110305-+_vXX.sav'
elif sitereq == 'mcgr':
    asifn = 'THEMIS/thg_l1_asf_mcgr_2013041408_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_mcgr_20110305-+_vXX.sav'
elif sitereq == 'inuv':
    asifn = 'THEMIS/thg_l1_asf_inuv_2013041408_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_inuv_20150401-+_vXX.sav'
elif sitereq == 'kian':
    asifn = 'THEMIS/thg_l1_ast_kian_20130414_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_kian_20111107-+_vXX.sav'
elif sitereq == 'whit':
    asifn = 'THEMIS/thg_l1_ast_whit_20130414_v01.cdf'
    asical = 'THEMIS/cal/themis_skymap_whit_20150814-+_vXX.sav'
else:
    raise ValueError(f'site {sitereq} not configured')

ocal = ['~/code/histfeas/precompute/hst0cal.h5',
        '~/code/histfeas/precompute/hst1cal.h5']

# %%
try:
    plotthemis(imgs, t, site, treq, moviefn, rows=R, cols=C,
               ext=(wC[0, 0], wC[0, -1], wR[-1, 0], wR[0, 0]))
except NameError:
    # 60 second computation
    imgs, R, C, t, site, wR, wC = altfiducial(asifn, asical, ocal, treq, odir)


show()
