# -*- coding: utf-8 -*-
import math
from datetime import datetime, timedelta, date, time
from pytz import timezone
import pysw
from utils import parsestrtime

def solar_rev(boss):
    date, time = parsestrtime(boss.state.curr_chart.date)
    d,m,y = [int(i) for i in date.split("/")]
    nowyear = boss.state.date.dt.year
    julday = pysw.julday(nowyear,m,d,0.0)
    sun = boss.state.curr_chart.planets[0]
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow > sun:
        julday -= 0.1
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow < sun:
        julday += 0.01
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)
    julday -= 0.01
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow < sun:
        julday += 0.001
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)
    julday -= 0.001
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow < sun:
        julday += 0.0001
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)
    julday -= 0.0001
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow < sun:
        julday += 0.00001
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)
    julday -= 0.00001
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    while sunnow < sun:
        julday += 0.000001
        s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)
    julday -= 0.000001
    s,sunnow,e = pysw.calc(julday,0,boss.state.epheflag)

    sol = pysw.revjul(julday)
    zone = boss.state.curr_chart.zone
    dt = boss.state.date.getnewdt(sol)
    boss.da.panel.set_date_only(dt)

def sec_prog(boss):
    chart = boss.state.curr_chart
    if not chart.date:
        chart = boss.state.now

    date = strdate_to_date(chart.date)
    nowyear = boss.state.date.dt.year
    birthyear = date.year
    yearsfrombirth = nowyear - birthyear
    progdate = date + timedelta(yearsfrombirth)

    if not boss.da.sec_alltimes:
        dt = combine_date(progdate)
        boss.state.calcdt.setdt(dt)
        boss.state.setprogchart(chart)
        birthday = synthbirthday(date,nowyear)
        boss.da.panel.set_date_only(birthday)
    else:
        nowdate = boss.state.date.dt
        prev_birthday = synthbirthday(date,nowyear)
        next_birthday = synthbirthday(date,nowyear+1)
        delta = nowdate - prev_birthday
        if delta.days < 0:
            next_birthday = prev_birthday
            prev_birthday = synthbirthday(date,nowyear-1)
            delta = nowdate - prev_birthday
            yearsfrombirth -= 1
        yeardelta = next_birthday - prev_birthday
        wholedelta = delta.days*86400+delta.seconds
        wholeyeardelta = yeardelta.days*86400+yeardelta.seconds
        frac = wholedelta/float(wholeyeardelta)
        oneday_ahead = date + timedelta(yearsfrombirth+1)
        daydelta = (oneday_ahead - progdate)
        daydelta = timedelta(daydelta.days*frac,daydelta.seconds*frac)
        inbetween_progdate = progdate + daydelta
        dt = combine_date(inbetween_progdate)
        boss.state.calcdt.setdt(dt)
        boss.state.setprogchart(chart)

#curr.setloc(city,code)
#curr.calcdt.setdt(datetime.datetime.combine(self.date,self.time))
#curr.setchart()

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
    return datetime(y,mo,d,int(h),m,0,tzinfo=timezone('UTC'))

def combine_date(dt):
    newdate = date(dt.year,dt.month,dt.day)
    newtime = time(dt.hour,dt.minute,dt.second)
    return datetime.combine(newdate,newtime)

def synthbirthday(date,nowyear):
    h = date.hour
    m = date.minute
    s = date.second
    y = nowyear
    mo = date.month
    d = date.day
    return datetime(y,mo,d,h,m,s,tzinfo=timezone('UTC'))
