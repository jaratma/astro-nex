# -*- coding: utf-8 -*-
import math
from datetime import datetime, timedelta, date, time
from pytz import timezone
RAD = math.pi / 180

class PersonInfo(object):
    count = 1
    def __init__(self):
        self.first = _("sin_nombre%d") % self.count
        self.last = ""

    def set_first(self,noname=False):
        if noname:
            self.first = ''
        else:
            self.first = _("sin_nombre%d") % self.count
            PersonInfo.count += 1


def degtodec(d):
    sign = 1
    if d.startswith('-'):
        sign = -sign
        d = d[1:]
    sec, rest = d[-2:], d[:-2]
    mint, deg = rest[-2:], rest[:-2]
    mint = int(mint) + int(sec)/60.0
    if not deg: deg = '0'
    deg = int(deg) + mint/60
    deg *= sign
    return deg

def dectodeg(d):
    import math
    sign = ''
    if d < 0 :  sign = '-'
    absd = abs(d)
    deg = int(math.floor(absd))
    rest = (absd - deg) * 60
    mint = int(math.floor(rest))
    sec = int(math.floor((rest - mint) * 60))
    return (sign+str(deg)+str(mint).zfill(2)+str(sec).zfill(2))

def parsestrtime(strdate):
    date,_,time = strdate.partition('T')
    date = "/".join(reversed(date.split('-'))) 
    zone, time  = time[8:], time[:5]
    try:
        zone.index(':')
        delta, zone = zone[:6], zone[6:]
    except ValueError:
        delta, zone = zone[:5], zone[5:]
        d1, d2 = delta[1:3], delta[3:5]
        delta = delta[0]+str(int(d1)+int(d2)).rjust(2,'0')
    time += ' '+delta+zone
    return (date, time)

        

def format_longitud(long):
    longitud = dectodeg(long)[:-2]
    if longitud[0] == '-':
        let = 'W'
        longitud = longitud[1:]
    else:
        let = 'E'
    return longitud[0:-2]+let+longitud[-2:]

def format_latitud(lat):
    latitud = dectodeg(lat)[:-2]
    if latitud[0] == '-':
        let = 'S'
        latitud = latitud[1:]
    else:
        let = 'N'
    return latitud[0:-2]+let+latitud[-2:]

def points_from_angle(angles):
    points = []
    for a in angles:
        points.append((math.cos(a*RAD),math.sin(a*RAD)))
    return points

def strdate_to_date(strdate):
    date,_,time = strdate.partition('T')
    try:
        y,mo,d = [ int(x) for x in date.split('-')]
    except ValueError:
        print date
    zone, time  = time[8:], time[:5]
    try:
        zone.index(':')
        delta, zone = zone[:6], zone[6:]
        d1, d2 = delta[1:3], delta[4:6]
        tot = int(d1)+int(d2)/60.0
    except ValueError:
        delta, zone = zone[:5], zone[5:]
        d1, d2 = delta[1:3], delta[3:5]
        tot = int(d1)+int(d2)
    sign = {'+': 1, '-': -1}[delta[0]]
    delta = tot*sign
    h,m = [int(x) for x in time.split(':')]
    #h = (h + m/60.0) - delta
    #m = int((h - int(h))*60)
    dt = datetime(y,mo,d,int(h),m,0,tzinfo=timezone('UTC'))
    dt = datetime.combine(dt.date(),dt.time())
    return dt
