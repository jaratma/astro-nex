# -*- coding: utf-8 -*-
from pytz.tzinfo import DstTzInfo
from datetime import datetime,timedelta

class Vienna(DstTzInfo):
    zone = 'Europe/Vienna'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1910, 5, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Brussels(DstTzInfo):
    zone = 'Europe/Brussels'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1880, 1, 1, 0),
            datetime(1892, 5, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 1020), timedelta(0), 'LMT'),
            (timedelta(0, 0), timedelta(0), 'CET') ]

class Zurich(DstTzInfo):
    zone = 'Europe/Zurich'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1851, 1, 1, 0),
            datetime(1894, 6, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 1800), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Prague(DstTzInfo):
    zone = 'Europe/Prague'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1891, 1, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Berlin(DstTzInfo):
    zone = 'Europe/Berlin'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1891, 3, 15, 0), 
            datetime(1893, 4, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 2220), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Copenhagen(DstTzInfo):
    zone = 'Europe/Copenhagen'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1894, 1, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class London(DstTzInfo):
    zone = 'Europe/London'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1880, 1, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 0), timedelta(0), 'GMT') ]

class Athens(DstTzInfo):
    zone = 'Europe/Athens'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1885, 9, 14, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 5700), timedelta(0), 'AMT') ]

class Rome(DstTzInfo):
    zone = 'Europe/Rome'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1893, 11, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Malta(DstTzInfo):
    zone = 'Europe/Malta'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1893, 11, 2, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Monaco(DstTzInfo):
    zone = 'Europe/Monaco'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1891, 3, 15, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 540), timedelta(0), 'PMT') ]

class Oslo(DstTzInfo):
    zone = 'Europe/Oslo'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1895, 5, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Amsterdam(DstTzInfo):
    zone = 'Europe/Amsterdam'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1892, 5, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 1200), timedelta(0), 'AMT') ]

class Lisbon(DstTzInfo):
    zone = 'Europe/Lisbon'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1884, 1, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(-1, 84180), timedelta(0), 'LMT') ]

class Warsaw(DstTzInfo):
    zone = 'Europe/Warsaw'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1891, 10, 1, 0) ]
    _transition_info = [
            (timedelta(0, 5040), timedelta(0), 'WMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

class Stockholm(DstTzInfo):
    zone = 'Europe/Stockholm'
    _utc_transition_times = [
            datetime(1, 1, 1, 0, 0),
            datetime(1878, 5, 31, 0, 0),
            datetime(1900, 1, 1, 0) ]
    _transition_info = [
            (timedelta(0, 0), timedelta(0), 'LMT'),
            (timedelta(0, 4680), timedelta(0), 'LMT'),
            (timedelta(0, 3600), timedelta(0), 'CET') ]

oldtimes = {
        'Europe/Zurich': Zurich,
        'Europe/Copenhagen': Copenhagen,
        'Europe/Prague': Prague,
        'Europe/Vienna': Vienna, 
        'Europe/Brussels': Brussels,
        'Europe/Berlin': Berlin,
        'Europe/London': London,
        'Europe/Athens': Athens,
        'Europe/Malta': Malta,
        'Europe/Monaco': Monaco,
        'Europe/Oslo': Oslo,
        'Europe/Amsterdam': Amsterdam,
        'Europe/Lisbon': Lisbon,
        'Europe/Rome': Rome,
        'Europe/Warsaw': Warsaw,
        'Europe/Stockholm': Stockholm
        }
