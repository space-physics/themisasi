#!/usr/bin/env python
import matplotlib
matplotlib.use('agg') 
from pathlib import Path
from numpy.testing import run_module_suite,assert_allclose
#
from themisasi import altfiducial
#from themisasi.plots import plotthemis
from themisasi.calread import calread

rdir = Path(__file__).parent

def test_calread():
    fn = rdir/'themis_skymap_gako_20110305-+_vXX.sav'
    az,el,lla,x,y = calread(fn)

    assert_allclose(15.458,el[29,161])
    assert_allclose(1.6255488,az[29,161])
    assert_allclose(214.83999634,lla['lon'])
    assert x[15,161] == 161
    assert y[15,161] == 15

if __name__ == '__main__':
   # test_calread()
    run_module_suite()
