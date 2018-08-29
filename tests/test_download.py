#!/usr/bin/env python
import themisasi as ta
import pytest
from pathlib import Path

R = Path(__file__).parent


def test_download():
    ta.download('2006-09-29T14', odir=R, site='gako',
                host='http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/')

    assert (R/'thg_l1_asf_gako_2006092914_v01.cdf').is_file()

    ta.download(('2006-09-29T14', '2006-09-30-04'), odir=R, site='gako',
                host='http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/')

    assert (R/'thg_l1_asf_gako_2006093004_v01.cdf').is_file()


if __name__ == '__main__':
    pytest.main([__file__])
