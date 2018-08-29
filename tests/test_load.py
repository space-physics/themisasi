#!/usr/bin/env python
from pathlib import Path
import pytest
from pytest import approx
import themisasi as ta
from datetime import datetime, timedelta
import tempfile
#
R = Path(__file__).parent
datfn = R / 'thg_l1_asf_gako_2011010617_v01.cdf'

cal1fn = R / 'themis_skymap_gako_20110305-+_vXX.sav'
cal2fn = R / 'thg_l2_asc_gako_19700101_v01.cdf'

assert datfn.is_file()
assert cal1fn.is_file()
assert cal2fn.is_file()


def test_read():
    with tempfile.NamedTemporaryFile() as f:
        bfn = f.name
        with pytest.raises(OSError):
            ta.load(bfn)

    with pytest.raises(FileNotFoundError):
        ta.load(bfn)

    data = ta.load(datfn)

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (23, 256, 256) and data['imgs'].dtype == 'uint16'


def test_read_timereq():
    dat = ta.load(datfn)
    times = dat.time.values

    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 18)).all()
# %% bad time requests
    with pytest.raises(TypeError):
        dat = ta.load(datfn, 1)

    with pytest.raises(ValueError):
        dat = ta.load(datfn, '2011-01-06T16:59:59')

    with pytest.raises(ValueError):
        dat = ta.load(datfn, '2011-01-06T18:00:01')
# %% good time requests
    dat = ta.load(datfn, '2011-01-06T17:00:12')
    assert dat['imgs'].shape[0] == 1
    time = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert time - datetime(2011, 1, 6, 17, 0, 12) < timedelta(seconds=0.02)

    dat = ta.load(datfn, ('2011-01-06T17:00:00', '2011-01-06T17:00:12'))
    assert dat['imgs'].shape[0] == 4
    time = dat.time.values.astype('datetime64[us]').astype(datetime)


@pytest.mark.filterwarnings('ignore:Not able to verify number of bytes from header')
def test_calread_idl():
    pytest.importorskip('scipy')

    cal1 = ta.loadcal(cal1fn)

    assert cal1['el'][29, 161] == approx(15.458)
    assert cal1['az'][29, 161] == approx(1.6255488)
    assert cal1.lon == approx(-145.16)


def test_calread_cdf():
    cal2 = ta.loadcal(cal2fn)

    assert cal2['el'][29, 161] == approx(19.132568)
    assert cal2['az'][29, 161] == approx(183.81241)
    assert cal2.lon == approx(-145.16)


if __name__ == '__main__':
    pytest.main(['-xrsv', __file__])
