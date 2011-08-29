#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import time
from datetime import timedelta


def pretty_time(utctime, tz=None):
    localtime = utctime + timedelta(hours=8)
    fmt = None
    if localtime.hour < 12:
        fmt = "%Y年%m月%d號 上午%I:%M:%S"
    else:
        fmt = "%Y年%m月%d號 下午%I:%M:%S"

    return {'iso8601': utctime.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'localized': localtime.strftime(fmt),
            'timestamp': int(time.mktime(utctime.timetuple())),
            }
