#!/usr/bin/env python
"""
example:
DownloadThemis 2012-11-03T06:23 2012-11-03T06:24 ~/data -s gako
"""
import themisasi.web as tweb
from argparse import ArgumentParser

VIDEO_BASE = 'http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/'
CAL_BASE = 'http://themis.ssl.berkeley.edu/data/themis/thg/l2/asi/cal/'


def main():
    p = ArgumentParser()
    p.add_argument('startend', help='start/end times UTC e.g. 2012-11-03T06:23 2012-11-03T06:24', nargs='+')
    p.add_argument('odir', help='directory to write downloaded CDF to')
    p.add_argument('-s', '--site', help='fykn gako etc.', nargs='+')
    p.add_argument('-overwrite', help='overwrite existing files', action='store_true')
    p.add_argument('-vh', help='Stem of URL for Video data', default=VIDEO_BASE)
    p.add_argument('-ch', help='Stem of URL for calibration data', default=CAL_BASE)

    P = p.parse_args()

    urls = {'video_stem': P.vh, 'cal_stem': P.ch}

    tweb.download(P.startend, P.site, P.odir, P.overwrite, urls)


if __name__ == '__main__':
    main()
