#!/usr/bin/env python
from pathlib import Path
import pytest
from pytest import approx
import themisasi as ta
from datetime import datetime, timedelta, date
import tempfile
#
R = Path(__file__).parent
datfn = R / 'thg_l1_asf_gako_2011010617_v01.cdf'

cal1fn = R / 'themis_skymap_gako_20110305-+_vXX.sav'
cal2fn = R / 'thg_l2_asc_gako_19700101_v01.cdf'

assert datfn.is_file()
assert cal1fn.is_file()
assert cal2fn.is_file()


def test_filename():
    with tempfile.NamedTemporaryFile() as f:
        bfn = f.name
        with pytest.raises(OSError):
            ta.load(bfn)

    with pytest.raises(FileNotFoundError):
        ta.load(bfn)

    data = ta.load(datfn)

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (23, 256, 256) and data['imgs'].dtype == 'uint16'


def test_filename_calname():

    with pytest.raises(ValueError):
        ta.load(datfn, calfn=cal1fn)

    data = ta.load(datfn, calfn=cal2fn)
    assert 'az' in data and 'el' in data
    assert data['az'].shape == data['imgs'].shape[1:]


def test_site():
    # %% load by filename
    dat = ta.load(datfn)
    times = dat.time.values

    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 18)).all()
# %% load by site/time
    dat = ta.load(R, 'gako', '2011-01-06T17:00:00')
    assert dat['imgs'].shape[0] == 1
    time = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert abs(time - datetime(2011, 1, 6, 17, 0, 0)) < timedelta(seconds=.5)

    dat = ta.load(R, 'gako', treq=('2011-01-06T17:00:00', '2011-01-06T17:00:12'))
    assert dat['imgs'].shape[0] == 4
    times = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 17, 0, 12)).all()

    ta.load(R, 'gako', treq=('2011-01-06T16:59:59', '2011-01-06T17:00:12'))
    assert dat['imgs'].shape[0] == 4
    times = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 17, 0, 12)).all()


def test_bad_time():
    with pytest.raises(TypeError):
        ta.load(datfn, treq=1)

    with pytest.raises(ValueError):
        ta.load(datfn, treq='2011-01-06T16:59:59')

    with pytest.raises(ValueError):
        ta.load(datfn, treq='2011-01-06T18:00:01')

    with pytest.raises(FileNotFoundError):
        ta.load(R, 'gako', treq='2010-01-01')

    with pytest.raises(FileNotFoundError):
        ta.load(R, 'gako', treq=('2010-01-01', '2010-01-01T01'))


def test_good_time():
    dat = ta.load(datfn, treq='2011-01-06T17:00:12')
    assert dat['imgs'].shape[0] == 1
    time = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert abs(time - datetime(2011, 1, 6, 17, 0, 12)) < timedelta(seconds=0.02)

    dat = ta.load(datfn, treq=('2011-01-06T17:00:00', '2011-01-06T17:00:12'))
    assert dat['imgs'].shape[0] == 4
    time = dat.time.values.astype('datetime64[us]').astype(datetime)


def test_calread_idl():

    cal = ta.loadcal(cal1fn)

    assert cal['el'][29, 161] == approx(15.458)
    assert cal['az'][29, 161] == approx(1.6255488)
    assert cal.lon == approx(-145.16)


def test_calread_cdf():
    cal = ta.loadcal(cal2fn)

    assert cal['el'][29, 161] == approx(19.132568)
    assert cal['az'][29, 161] == approx(183.81241)
    assert cal.lon == approx(-145.16)


def test_calread_sitedate():

    cal = ta.loadcal(R, 'gako', '2011-01-06')
    assert cal.caltime.date() == date(2007, 2, 2)


if __name__ == '__main__':
    pytest.main(['-xrsv', __file__])
