#!/usr/bin/env python
from pathlib import Path
import numpy as np
import unittest
#
import themisasi as tasi
import themisasi.calread
#
R = Path(__file__).parent
datfn = R / 'thg_l1_ast_gako_20110505_v01.cdf'
calfn = R / 'themis_skymap_gako_20110305-+_vXX.sav'

class BasicTests(unittest.TestCase):

    def test_readthemis(self):
        dat = tasi.readthemis(datfn)

    def test_calread(self):

        az,el,lla,x,y = tasi.calread.calread(calfn)

        np.testing.assert_allclose(15.458,el[29,161])
        np.testing.assert_allclose(1.6255488,az[29,161])
        np.testing.assert_allclose(214.83999634,lla['lon'])
        assert x[15,161] == 161
        assert y[15,161] == 15


if __name__ == '__main__':
     unittest.main()
