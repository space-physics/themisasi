#!/usr/bin/env python
from pathlib import Path
import numpy as np
#
import themisasi as ta
#
R = Path(__file__).parent
datfn = R / 'thg_l1_ast_gako_20110505_v01.cdf'
calfn = R / 'themis_skymap_gako_20110305-+_vXX.sav'

assert datfn.is_file()
assert calfn.is_file()


def test_readthemis():
    data = ta.load(datfn, fullthumb='t')

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (
        1075, 32, 32) and data['imgs'].dtype == np.uint16


def test_calread():

    cal = ta.loadcal(calfn)

    np.testing.assert_allclose(cal['el'][29, 161], 15.458)
    np.testing.assert_allclose(cal['az'][29, 161], 1.6255488)
    np.testing.assert_allclose(cal.lon, -145.16)


if __name__ == '__main__':
    np.testing.run_module_suite()
