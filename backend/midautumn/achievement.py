#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
import time
from datetime import date, timedelta
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext import db
from django.utils import simplejson as json
from midautumn.models import FacebookUser


ITEM_OFFSET = 1000
ITEM_COUNT_OFFSET = 2000
TIME_OFFSET = 3000
LIKE_COUNT_OFFSET = 4000
COMMENT_COUNT_OFFSET = 5000
CONTINUOUS_VISIT_OFFSET = 6000
LAST_OFFSET = 7000

ITEM_KEY = [u'玉米', u'臭豆腐', u'可樂', u'流星下的怨', u'星光戰士舞', u'Cloony 是大帥哥', ]
ITEM_VALUE = {
    u'玉米': (u'Ron 的最愛。', 'corn.png'),
    u'臭豆腐': (u'臭豆腐怎麼烤啊？', 'stinky-tofu.png'),
    u'可樂': (u'俊輝的最愛。', 'coke.png'),
    u'流星下的怨': (u'Cloony 和 San 的經典。', 'meteor.png'),
    u'星光戰士舞': (u'Leo 的代表作。', 'starlight-warrior.png'),
    u'Cloony 是大帥哥': (u'...', 'cloony-toro.png'),
    }

ITEM_COUNT_VALUE = {
    1: (u'第一個物品', u'恭喜你推薦了你的第一個物品。', 'item-count-1.png'),
    5: (u'第五個物品', u'恭喜你推薦了你的第五個物品。', 'item-count-5.png'),
    10: (u'第十個物品', u'恭喜你推薦了你的第十個物品。', 'item-count-10.png'),
    50: (u'第五十個物品', u'太誇張了！你推薦了你的第五十個物品。', 'item-count-50.png'),
    100: (u'第一百個物品', u'你贏了！你推薦了你的第一百個物品。', 'item-count-100.png'),
    500: (u'第五百個物品', u'真有毅力！你推薦了你的第五百個物品。', 'item-count-500.png'),
    }

TIME_KEY = [date(2011, 9, 12), date(2012, 9, 13),
            date(2011, 12, 25), date(2012, 12, 25),
            date(2012, 1, 1), date(2013, 1, 1),
            date(2012, 1, 23), date(2013, 2, 10),
            ]
TIME_VALUE = {
    date(2011, 9, 12): (u'中秋節 2011', u'中秋節快樂。', 'midautumn2011.png'),
    date(2012, 9, 13): (u'中秋節 2012', u'中秋節快樂。', 'midautumn2012.png'),
    date(2011, 12, 25): (u'聖誕節 2011', u'聖誕節快樂。', 'christmas2011.png'),
    date(2012, 12, 25): (u'聖誕節 2012', u'聖誕節快樂。', 'christmas2012.png'),
    date(2012, 1, 1): (u'新年 2012', u'新年快樂。', 'newyear2012.png'),
    date(2013, 1, 1): (u'新年 2013', u'新年快樂。', 'newyear2013.png'),
    date(2012, 1, 23): (u'農曆新年 2012', u'農曆新年快樂。', 'lunarnewyear2012.png'),
    date(2013, 2, 10): (u'農曆新年 2013', u'農曆新年快樂。', 'lunarnewyear2013.png'),
    }

LIKE_COUNT_VALUE = {
    1: (u'第一個讚', u'送出了第一個讚。', 'like-count-1.png'),
    5: (u'第五個讚', u'送出了第五個讚。', 'like-count-5.png'),
    10: (u'第十個讚', u'送出了第十個讚。', 'like-count-10.png'),
    50: (u'第五十個讚', u'太誇張了！送出了第五十個讚。', 'like-count-50.png'),
    100: (u'第一百個讚', u'你贏了！送出了第一百個讚。', 'like-count-100.png'),
    500: (u'第五百個讚', u'真有毅力！送出了第五百個讚。', 'like-count-500.png'),
}

COMMENT_COUNT_VALUE = {
    1: (u'第一個留言', u'送出了第一個留言。', 'comment-count-1.png'),
    5: (u'第五個留言', u'送出了第五個留言。', 'comment-count-5.png'),
    10: (u'第十個留言', u'送出了第十個留言。', 'comment-count-10.png'),
    50: (u'第五十個留言', u'太誇張了！送出了第五十個留言。', 'comment-count-50.png'),
    100: (u'第一百個留言', u'你贏了！送出了第一百個留言。', 'comment-count-100.png'),
    500: (u'第五百個留言', u'真有毅力！送出了第五百個留言。', 'comment-count-500.png'),
}

CONTINUOUS_VISIT_KEY = [2, 7, 30, 365]
CONTINUOUS_VISIT_VALUE = {
    2: (u'連續兩天', u'連續兩天光臨。', 'continuous-visit-count-2.png'),
    7: (u'連續一禮拜', u'連續一禮拜光臨。', 'continuous-visit-count-7.png'),
    30: (u'連續一個月', u'連續一個月光臨。', 'continuous-visit-count-30.png'),
    365: (u'連續一年', u'你贏了！連續一年光臨。', 'continuous-visit-count-365.png'),
}


class UserAchievement(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='achievement_set', required=True)
    achievement_id = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @property
    def info(self):
        aid = self.achievement_id
        title, description, icon = None, None, None

        if aid >= LAST_OFFSET:
            pass
        elif aid >= CONTINUOUS_VISIT_OFFSET:
            key = aid - CONTINUOUS_VISIT_OFFSET
            if key in CONTINUOUS_VISIT_VALUE:
                title, description, icon = CONTINUOUS_VISIT_VALUE[key]
        elif aid >= COMMENT_COUNT_OFFSET:
            key = aid - COMMENT_COUNT_OFFSET
            if key in COMMENT_COUNT_VALUE:
                title, description, icon = COMMENT_COUNT_VALUE[key]
        elif aid >= LIKE_COUNT_OFFSET:
            key = aid - LIKE_COUNT_OFFSET
            if key in LIKE_COUNT_VALUE:
                title, description, icon = LIKE_COUNT_VALUE[key]
        elif aid >= TIME_OFFSET:
            idx = aid - TIME_OFFSET
            if idx < len(TIME_KEY):
                key = TIME_KEY[idx]
                if key in TIME_VALUE:
                    title, description, icon = TIME_VALUE[key]
        elif aid >= ITEM_COUNT_OFFSET:
            key = aid - ITEM_COUNT_OFFSET
            if key in ITEM_COUNT_VALUE:
                title, description, icon = ITEM_COUNT_VALUE[key]
        elif aid >= ITEM_OFFSET:
            idx = aid - ITEM_OFFSET
            if idx < len(ITEM_KEY):
                key = ITEM_KEY[idx]
                if key in ITEM_VALUE:
                    title = key
                    description, icon = ITEM_VALUE[key]
        else:
            pass

        if title and description and icon:
            relative_url = '/img/' + icon
            return {'title': title,
                    'description': description,
                    'icon_url': relative_url,
                    'icon_absolute_url': 'http://midautumn.ronhuang.org' + relative_url,
                    }
        else:
            return {}


    # for serialization
    def to_dict(self):
        localtime = self.created + timedelta(hours=8)
        fmt = None
        if localtime.hour < 12:
            fmt = "%Y年%m月%d號 上午%I:%M:%S"
        else:
            fmt = "%Y年%m月%d號 下午%I:%M:%S"

        relative_url = '/achievement/%s' % self.key().id()
        result = {'created_iso8601': self.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
                  'created_local': localtime.strftime(fmt),
                  'relative_url': relative_url,
                  'absolute_url': 'http://midautumn.ronhuang.org' + relative_url,
                  }

        # update result with actual achievement info
        result.update(self.info)

        return result


def _check_item(obj):
    title = obj.title
    owner = obj.owner

    if title not in ITEM_KEY:
        return []

    achievement_id = ITEM_OFFSET + ITEM_KEY.index(title)

    # check if already received achievement
    query = owner.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    description, icon = ITEM_VALUE[title]
    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]

def _check_item_count(obj):
    owner = obj.owner

    count = owner.object_set.count()

    if count not in ITEM_COUNT_VALUE:
        return []

    achievement_id = ITEM_COUNT_OFFSET + count

    # check if already received achievement
    query = owner.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = ITEM_COUNT_VALUE[count]
    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]

def check_post(obj):
    achievements = []
    achievements.extend(_check_item(obj))
    achievements.extend(_check_item_count(obj))
    return achievements


def check_like():
    pass


def check_comment():
    pass


def check_continuous_visit(user):
    count = user.continuous_visit_count
    if count not in CONTINUOUS_VISIT_VALUE:
        return []

    achievement_id = CONTINUOUS_VISIT_OFFSET + count

    # check if already received achievement
    query = user.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=user, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = CONTINUOUS_VISIT_VALUE[count]
    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]
