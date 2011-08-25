#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


import datetime


class TPE(datetime.tzinfo):
    "Time zone for Taipei"

    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "Asia/Taipei"
