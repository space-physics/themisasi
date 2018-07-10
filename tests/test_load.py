#!/usr/bin/env python
from pathlib import Path
import pytest
import numpy as np
from numpy.testing import assert_allclose
#
import themisasi as ta
#
R = Path(__file__).parent
datfn = R / 'thg_l1_ast_gako_20110505_v01.cdf'

cal1fn = R / 'themis_skymap_gako_20110305-+_vXX.sav'
cal2fn = R / 'thg_l2_asc_gako_19700101_v01.cdf'

assert datfn.is_file()
assert cal1fn.is_file()
assert cal2fn.is_file()


def test_readthemis():
    data = ta.load(datfn)

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (1075, 32, 32) and data['imgs'].dtype == np.uint16


def test_calread():
    # %% IDL SAV
    cal1 = ta.loadcal(cal1fn)

    assert_allclose(cal1['el'][29, 161], 15.458)
    assert_allclose(cal1['az'][29, 161], 1.6255488)
    assert_allclose(cal1.lon, -145.16)
# %% CDF
    cal2 = ta.loadcal(cal2fn)

    assert_allclose(cal2['el'][29, 161], 19.132568)
    assert_allclose(cal2['az'][29, 161], 183.81241)
    assert_allclose(cal2.lon, -145.16)


if __name__ == '__main__':
    pytest.main()
