# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, tzinfo
from pytz import timezone
from bisect import bisect_right
from tz_sup import oldtimes

_cache = {}

class NeXDate(object):
    '''Date/time settings'''
    def __init__(self,current,dt=datetime.now(), tz=timezone('UTC')):
        self.tz = tz
        self.ld = self.tz.localize(dt, is_dst=True)
        self.dt = self.ld.astimezone(timezone('UTC'))
        self.current = current

    def patch_timezone(self,tz):
        tz = tz.encode('US-ASCII')
        if not tz in oldtimes:
            return timezone(tz)
        else:
            try:
                return _cache[tz]
            except KeyError:
                z = oldtimes[tz]()
                ptz = timezone(tz)
                ptz._utc_transition_times[:1] = z._utc_transition_times
                ptz._transition_info[:1] = z._transition_info 
                ptz._tzinfos.update(z._tzinfos)
                _cache[tz] = ptz
                return ptz 

    def settz(self, tz):
        # we need a naive datetime object
        self.tz = self.patch_timezone(tz)
        dt = self.ld.combine(self.ld.date(), self.ld.time())
        if bisect_right(self.tz._utc_transition_times, dt) == 1:
            offset = round(self.current.loc.longdec*4)
            tzLong = FixedOffset(offset)
            self.ld = tzLong.localize(dt, is_dst=True)
            self.dt = self.ld.astimezone(timezone('UTC'))
        else: 
            self.ld = self.tz.localize(dt, is_dst=True)
            self.dt = self.ld.astimezone(timezone('UTC'))
    
    def setdt(self, dt):
        #print dt, self.tz
        if bisect_right(self.tz._utc_transition_times, dt) == 1:
            offset = round(self.current.loc.longdec*4)
            tzLong = FixedOffset(offset)
            self.ld = tzLong.localize(dt, is_dst=True)
            self.dt = self.ld.astimezone(timezone('UTC'))
        else: 
            self.ld = self.tz.localize(dt, is_dst=True)
            self.dt = self.ld.astimezone(timezone('UTC'))

    def set_now(self):
        self.setdt(datetime.now())

    def getnewdt(self,dateset):
        y,m,d,h = dateset
        ho = int(h)
        mi = ((h - ho) * 60)
        se = int((mi - int(mi)) * 60)
        mi = int(mi)
        dt = datetime(y,m,d,ho,mi,se,tzinfo=timezone('utc'))
        loc = dt.astimezone(self.tz)
        return loc

    def set_delta(self, delta,getback=False):
        amount = delta[0]
        what = delta[1]
        dt = self.ld.combine(self.ld.date(), self.ld.time())
        if what == 'minutes':
            dt = dt + timedelta(minutes=amount)
        elif what == 'hours':
            dt = dt + timedelta(hours=amount)
        elif what == 'days':
            dt = dt + timedelta(days=amount)
        elif what == 'month':
            change = dt.month+amount
            if change < 1:
                y = dt.year-1; m = 12+change
            elif change > 12:
                y = dt.year+1; m = change-12
            else: 
                y = dt.year; m = change
            try: 
                dt = dt.replace(year=y, month=m)
            except ValueError:
                try: 
                    dt = dt.replace(year=y, month=m, day=dt.day-1)
                except ValueError:
                    dt = dt.replace(year=y, month=m, day=dt.day-2)#February 
        elif what == 'year':
            dt = dt.replace(year=(dt.year+amount))
        if not getback:
            self.setdt(dt)
        else:
            return dt

    def dateforcalc(self):
        t = self.dt.time()
        m = t.minute + t.second/60.0
        h = t.hour + m/60.0
        y = self.dt.year
        m = self.dt.month
        d = self.dt.day
        return y, m, d, h

    def dateforstore(self):
        if self.ld.year < 1900:
            y = self.ld.year
            mth = str(self.ld.month).rjust(2,'0')
            day = str(self.ld.day).rjust(2,'0')
            hour = str(self.ld.hour).rjust(2,'0')
            minute = str(self.ld.minute).rjust(2,'0')
            sec = str(self.ld.second).rjust(2,'0')
            zname = self.ld.tzname()
            print "here %s" % zname
            td = self.ld.utcoffset()
            d, s = td.days, td.seconds
            if d < 0:
                sign = '-'
                s = 86400 - s
            else: 
                sign = '+'
            m = s / 60
            h = sign + str(m / 60).rjust(2,'0')
            if m % 60 != 0:
                h += ':'+str(m%60).rjust(2,'0')
            else:
                h += '00'
            strdate = "%s-%s-%sT%s:%s:%s%s%s" % (y, mth, day, hour, minute, sec, h, zname) 
            return strdate
        else:
            return self.ld.strftime('%Y-%m-%dT%H:%M:%S%z%Z')

class FixedOffset(tzinfo):
    zone = 'LMT' # to match the standard pytz API

    def __init__(self, minutes):
        if abs(minutes) >= 1440:
            raise ValueError("absolute offset is too large", minutes)
        self._minutes = minutes
        self._offset = timedelta(minutes=minutes)

    def utcoffset(self, dt):
        return self._offset

    def __reduce__(self):
        return FixedOffset, (self._minutes, )

    def dst(self, dt):
        return None
    
    def tzname(self, dt):
        return FixedOffset.zone

    def __repr__(self):
        return 'pytz.FixedOffset(%d)' % self._minutes

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError, 'Not naive datetime (tzinfo is already set)'
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is None:
            raise ValueError, 'Naive time - no tzinfo set'
        return dt.replace(tzinfo=self)
