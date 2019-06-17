#!/usr/bin/env python
import themisasi.web as tw
import pytest
from pathlib import Path
import requests.exceptions

R = Path(__file__).parent

VIDEO_BASE = 'http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/'
CAL_BASE = 'http://themis.ssl.berkeley.edu/data/themis/thg/l2/asi/cal/'
urls = {'video_stem': VIDEO_BASE, 'cal_stem': CAL_BASE}


def test_single_time_site():
    try:
        tw.download('2006-09-29T14', 'gako', R, urls)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')

    assert (R/'thg_l1_asf_gako_2006092914_v01.cdf').is_file()
    assert (R/'thg_l2_asc_gako_19700101_v01.cdf').is_file()


@pytest.mark.asyncio
async def test_cal():
    try:
        await tw._download_cal('inuv', R, urls['cal_stem'])
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')


def test_time_range():
    try:
        tw.download(('2006-09-29T14', '2006-09-30-04'), 'gako', R, urls)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')

    assert (R/'thg_l1_asf_gako_2006093004_v01.cdf').is_file()
    assert (R/'thg_l2_asc_gako_19700101_v01.cdf').is_file()


def test_multi_site():
    try:
        tw.download('2006-09-30-04', ['gako', 'fykn'], R, urls)
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
        tw.download(time, site, R, urls)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')


if __name__ == '__main__':
    pytest.main([__file__])
