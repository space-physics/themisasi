#!/usr/bin/env python
from pathlib import Path
import pytest
from pytest import approx
import themisasi.io as tio
import themisasi as ta
#
R = Path(__file__).parent
datfn = R / 'thg_l1_ast_gako_20110505_v01.cdf'

cal1fn = R / 'themis_skymap_gako_20110305-+_vXX.sav'
cal2fn = R / 'thg_l2_asc_gako_19700101_v01.cdf'

assert datfn.is_file()
assert cal1fn.is_file()
assert cal2fn.is_file()


def test_download(tmpdir):
    ta.download(['2012-08-08T10', '2012-08-08T11'], odir=tmpdir, site='gako',
                host='http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/')


def test_read():
    data = tio.load(datfn)

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (1075, 32, 32) and data['imgs'].dtype == 'uint16'


@pytest.mark.filterwarnings('ignore:Not able to verify number of bytes from header')
def test_calread_idl():

    cal1 = tio.loadcal(cal1fn)

    assert cal1['el'][29, 161] == approx(15.458)
    assert cal1['az'][29, 161] == approx(1.6255488)
    assert cal1.lon == approx(-145.16)


def test_calread_cdf():
    cal2 = tio.loadcal(cal2fn)

    assert cal2['el'][29, 161] == approx(19.132568)
    assert cal2['az'][29, 161] == approx(183.81241)
    assert cal2.lon == approx(-145.16)


if __name__ == '__main__':
    pytest.main(['-x', __file__])
