#!/usr/bin/env python
import themisasi as ta
import themisasi.web as tw
import pytest
from pathlib import Path
import requests.exceptions

R = Path(__file__).parent


def test_single_time_site():
    try:
        ta.download('2006-09-29T14', 'gako', R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')

    assert (R/'thg_l1_asf_gako_2006092914_v01.cdf').is_file()
    assert (R/'thg_l2_asc_gako_19700101_v01.cdf').is_file()


def test_cal():
    try:
        tw._download_cal('inuv', R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')


def test_time_range():
    try:
        ta.download(('2006-09-29T14', '2006-09-30-04'), 'gako', R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')

    assert (R/'thg_l1_asf_gako_2006093004_v01.cdf').is_file()
    assert (R/'thg_l2_asc_gako_19700101_v01.cdf').is_file()


def test_multi_site():
    try:
        ta.download('2006-09-30-04', ['gako', 'fykn'], R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')

    assert (R/'thg_l1_asf_gako_2006093004_v01.cdf').is_file()
    assert (R/'thg_l2_asc_gako_19700101_v01.cdf').is_file()

    assert (R/'thg_l1_asf_fykn_2006093004_v01.cdf').is_file()
    assert (R/'thg_l2_asc_fykn_19700101_v01.cdf').is_file()


@pytest.mark.parametrize('time, site', [('2006-09-29T14', 'badname'),
                                        ('1950-01-01T01', 'gako')])
def test_nonexisting(time, site):
    try:
        ta.download(time, site, R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')


if __name__ == '__main__':
    pytest.main([__file__])
