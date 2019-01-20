#!/usr/bin/env python
from pathlib import Path
import pytest
from pytest import approx
import themisasi as ta
from datetime import datetime, timedelta, date
#
R = Path(__file__).parent
datfn = R / 'thg_l1_asf_gako_2011010617_v01.cdf'

cal1fn = R / 'themis_skymap_gako_20110305-+_vXX.sav'
cal2fn = R / 'thg_l2_asc_gako_19700101_v01.cdf'

assert datfn.is_file()
assert cal1fn.is_file()
assert cal2fn.is_file()


def test_missing_file(tmp_path):
    badfn = tmp_path / 'notafile.cdf'
    with pytest.raises(FileNotFoundError):
        ta.load(badfn)


def test_filename():
    data = ta.load(datfn)

    assert data['imgs'].site == 'gako'
    assert data['imgs'].shape == (23, 256, 256) and data['imgs'].dtype == 'uint16'


def test_filename_calname():

    with pytest.raises(ValueError):
        ta.load(datfn, calfn=cal1fn)

    data = ta.load(datfn, calfn=cal2fn)
    assert 'az' in data and 'el' in data
    assert data['az'].shape == data['imgs'].shape[1:]


def test_load_filename():
    """load by filename"""
    dat = ta.load(datfn)
    times = dat.time.values.astype('datetime64[us]').astype(datetime)

    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 18)).all()


@pytest.mark.parametrize('site, time', [('gako', '2011-01-06T17:00:00'),
                                        ('gako', datetime(2011, 1, 6, 17))])
def test_load_site_time(site, time):
    """ load by sitename + time"""
    dat = ta.load(R, site, time)
    assert dat['imgs'].shape[0] == 1
    t = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert abs(t - datetime(2011, 1, 6, 17, 0, 0)) < timedelta(seconds=.5)


@pytest.mark.parametrize('site, treq', [('gako', ('2011-01-06T17:00:00', '2011-01-06T17:00:12')),
                                        ('gako', ('2011-01-06T16:59:59', '2011-01-06T17:00:12'))])
def test_load_site_timerange(site, treq):
    """ load by sitename + timerange """
    dat = ta.load(R, site, treq=treq)
    assert dat['imgs'].shape[0] == 4
    times = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert (times >= datetime(2011, 1, 6, 17)).all()
    assert (times <= datetime(2011, 1, 6, 17, 0, 12)).all()


@pytest.mark.parametrize('path, val, err', [(datfn, 1, TypeError),
                                            (datfn, '2011-01-06T16:59:59', ValueError),
                                            (datfn, '2011-01-06T18:00:01', ValueError),
                                            (R, '2010-01-01', FileNotFoundError),
                                            (R, ('2010-01-01', '2010-01-01T01'), FileNotFoundError)
                                            ])
def test_bad_time(path, val, err):
    with pytest.raises(err):
        ta.load(path, 'gako', treq=val)


def test_good_time():
    dat = ta.load(datfn, treq='2011-01-06T17:00:12')
    assert dat['imgs'].shape[0] == 1
    time = dat.time.values.astype('datetime64[us]').astype(datetime)
    assert abs(time - datetime(2011, 1, 6, 17, 0, 12)) < timedelta(seconds=0.02)

    dat = ta.load(datfn, treq=('2011-01-06T17:00:00', '2011-01-06T17:00:12'))
    assert dat['imgs'].shape[0] == 4
    time = dat.time.values.astype('datetime64[us]').astype(datetime)


def test_autoload_cal():
    dat = ta.load(R, 'gako', '2011-01-06T17:00:00')
    assert 'el' in dat and 'az' in dat


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
