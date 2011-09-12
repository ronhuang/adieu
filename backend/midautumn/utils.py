#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import time
from datetime import timedelta, tzinfo, datetime


ZERO = timedelta(0)

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

utc = UTC()

class TPE(tzinfo):
    """Time zone for Taipei"""

    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return "Asia/Taipei"

tpe = TPE()

def pretty_time(dt, tz=tpe):
    utctime = None
    if not dt.tzname():
        # dt is naive, assume it's UTC
        utctime = dt.replace(tzinfo=utc)
    else:
        utctime = dt.astimezone(utc)

    localtime = utctime.astimezone(tz)

    fmt = None
    if localtime.hour < 12:
        fmt = "%Y年%m月%d號 上午%I:%M:%S"
    else:
        fmt = "%Y年%m月%d號 下午%I:%M:%S"

    return {'iso8601': utctime.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'localized': localtime.strftime(fmt),
            'timestamp': int(time.mktime(utctime.timetuple())),
            }

def localdate(tz=tpe):
    now = datetime.now(tz)
    return now.date()
