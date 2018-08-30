#!/usr/bin/env python
import pytest
import subprocess
from pathlib import Path

R = Path(__file__).parent


def test_video():
    pytest.importorskip('matplotlib')
    subprocess.check_call(['PlotThemis', str(R), 'gako',
                           '2011-01-06T17:00:03'])


def test_pixels_azel():
    pytest.importorskip('histutils')
    pytest.importorskip('matplotlib')
    subprocess.check_call(['PlotThemisPixels', str(R), 'gako',
                           '2011-01-06T17:00:00', '2011-01-06T17:00:06',
                           '-az', '65', '70', '-el', '48', '68'])


def test_pixels_latlon():
    pytest.importorskip('histutils')
    pytest.importorskip('matplotlib')
    subprocess.check_call(['PlotThemisPixels', str(R), 'gako',
                           '2011-01-06T17:00:00', '2011-01-06T17:00:06',
                           '-lla', '68', '-145', '100.'])


if __name__ == '__main__':
    pytest.main(['-xrsv', __file__])
