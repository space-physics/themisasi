#!/usr/bin/env python3
"""
Reads THEMIS ASI images 256x256 pixels
Michael Hirsch
"""
from dateutil.parser import parse
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve
def loaddata(site,dtime):
    url,htmlfn = urlbuild(site,dtime)
    try:
        urlretrieve(url,htmlfn)
    except Exception:
        print(url)

def urlbuild(site,dtime):
    url = 'http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/'
    url += site+'/{:d}/{:02d}/'.format(dtime.year,dtime.month)
    file = 'thg_l1_asf_{}_{}_v01.cdf'.format(site, dtime.strftime('%Y%m%d%H'))
    return url+file,file

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='simple loader of THEMIS ASI CDF files')
    p.add_argument('site',help='THEMIS site to load',type=str,nargs='?',default='fykn')
    p.add_argument('datetime',help='time of THEMIS data to load %y-%m-%dT%H:%M:%SZ',type=str)
    p = p.parse_args()

    dtime = parse(p.datetime)

    loaddata(p.site,dtime)