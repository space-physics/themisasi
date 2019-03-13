#!/usr/bin/env python
"""
example:
DownloadThemis 2012-11-03T06:23 2012-11-03T06:24 ~/data -s gako
"""
import themisasi as ta
from argparse import ArgumentParser


def main():
    p = ArgumentParser()
    p.add_argument('startend', help='start/end times UTC e.g. 2012-11-03T06:23 2012-11-03T06:24', nargs='+')
    p.add_argument('odir', help='directory to write downloaded CDF to')
    p.add_argument('-s', '--site', help='fykn gako etc.', nargs='+')
    p.add_argument('-overwrite', help='overwrite existing files', action='store_true')
    p.add_argument('-host', default='http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/')

    p = p.parse_args()

    ta.download(p.startend, p.site, p.odir, p.overwrite, p.host)


if __name__ == '__main__':
    main()
