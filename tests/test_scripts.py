#!/usr/bin/env python
import pytest
import subprocess
from pathlib import Path

R = Path(__file__).parent
datfn = R / 'thg_l1_ast_gako_20110505_v01.cdf'
calfn = R / 'thg_l2_asc_gako_19700101_v01.cdf'


def test_video():
    subprocess.check_call(['PlotThemis', str(datfn), str(calfn),
                           '--treq', '2011-05-05T09:47:00', '2011-05-05T09:47:10'])


def test_pixels_azel():
    pytest.importorskip('histutils')
    subprocess.check_call(['PlotThemisPixels', str(datfn), str(calfn),
                           '-az', '65', '70', '-el', '48', '68'])


def test_pixels_latlon():
    pytest.importorskip('histutils')
    subprocess.check_call(['PlotThemisPixels', str(datfn), str(calfn),
                           '-lla', '68', '-145', '100.'])


if __name__ == '__main__':
    pytest.main(['-x', __file__])
