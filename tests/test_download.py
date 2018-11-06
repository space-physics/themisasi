#!/usr/bin/env python
import themisasi as ta
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
        ta.download_cal('inuv', R)
    except requests.exceptions.ConnectionError:
        pytest.xfail('bad internet connection')


def test_time_range():
    with pytest.warns(UserWarning) as w:
        try:
            ta.download(('2006-09-29T14', '2006-09-30-04'), 'gako', R)
        except requests.exceptions.ConnectionError:
            pytest.xfail('bad internet connection')

        assert len(w) == 13  # 13 missing times

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


def test_nonexisting():
    with pytest.warns(UserWarning) as w:
        try:
            ta.download('2006-09-29T14', 'badsitename', R)
        except requests.exceptions.ConnectionError:
            pytest.xfail('bad internet connection')

        assert len(w) in (1, 2)

    with pytest.warns(UserWarning) as w:
        try:
            ta.download('1950-01-01T01', 'gako', R)
        except requests.exceptions.ConnectionError:
            pytest.xfail('bad internet connection')

        assert len(w) in (1, 2)


if __name__ == '__main__':
    pytest.main([__file__])
