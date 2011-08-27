#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
from datetime import date
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext import db
from django.utils import simplejson as json
from midautumn.models import MidautumnObject, UserAchievement


ITEM_OFFSET = 1000
ITEM_COUNT_OFFSET = 2000
TIME_OFFSET = 3000
LIKE_OFFSET = 4000
UNLIKE_OFFSET = 5000
COMMENT_OFFSET = 6000
UNCOMMENT_OFFSET = 7000
CONTINOUS_VISIT_OFFSET = 8000


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
    date(2012, 1, 1): (u'新年 2011', u'新年快樂。', 'newyear2012.png'),
    date(2013, 1, 1): (u'新年 2011', u'新年快樂。', 'newyear2013.png'),
    date(2012, 1, 23): (u'農曆新年 2011', u'農曆新年快樂。', 'lunarnewyear2012.png'),
    date(2013, 2, 10): (u'農曆新年 2011', u'農曆新年快樂。', 'lunarnewyear2013.png'),
    }

LIKED_COUNT_VALUE = {
    1: (u'第一個讚', u'送出了第一個讚。', 'like-count-1.png'),
    5: (u'第五個讚', u'送出了第五個讚。', 'like-count-5.png'),
    10: (u'第十個讚', u'送出了第十個讚。', 'like-count-10.png'),
    50: (u'第五十個讚', u'太誇張了！送出了第五十個讚。', 'like-count-50.png'),
    100: (u'第一百個讚', u'你贏了！送出了第一百個讚。', 'like-count-100.png'),
    500: (u'第五百個讚', u'真有毅力！送出了第五百個讚。', 'like-count-500.png'),
}

COMMENT_COUNT_VALUE = {
    1: (u'第一個註解', u'送出了第一個註解。', 'comment-count-1.png'),
    5: (u'第五個註解', u'送出了第五個註解。', 'comment-count-5.png'),
    10: (u'第十個註解', u'送出了第十個註解。', 'comment-count-10.png'),
    50: (u'第五十個註解', u'太誇張了！送出了第五十個註解。', 'comment-count-50.png'),
    100: (u'第一百個註解', u'你贏了！送出了第一百個註解。', 'comment-count-100.png'),
    500: (u'第五百個註解', u'真有毅力！送出了第五百個註解。', 'comment-count-500.png'),
}

CONTINUOUS_VISIT_COUNT_VALUE = {
    2: (u'連續兩天', u'連續兩天光臨。', 'continuous-visit-count-2.png'),
    7: (u'連續一禮拜', u'連續一禮拜光臨。', 'continuous-visit-count-7.png'),
    30: (u'連續一個月', u'連續一個月光臨。', 'continuous-visit-count-30.png'),
    365: (u'連續一年', u'你贏了！連續一年光臨。', 'continuous-visit-count-365.png'),
}


def _check_item(obj):
    title = obj.title
    owner = obj.owner

    if title not in ITEM_KEY:
        return []

    achievement_id = ITEM_OFFSET + ITEM_KEY.index(title)

    # check if already received achievement
    query = UserAchievement.gql('WHERE owner = :1 AND achievement_id = :2', owner, achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    description, icon = ITEM_VALUE[title]
    return [{'key': key.id(), 'title': title, 'description': description, 'icon': icon}]

def _check_item_count(obj):
    owner = obj.owner

    query = MidautumnObject.gql('WHERE owner = :1', owner)
    count = query.count()

    if count not in (1, 5, 10, 50, 100, 500):
        return []

    achievement_id = ITEM_COUNT_OFFSET + count

    # check if already received achievement
    query = UserAchievement.gql('WHERE owner = :1 AND achievement_id = :2', owner, achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = ITEM_COUNT_VALUE[count]
    return [{'key': key.id(), 'title': title, 'description': description, 'icon': icon}]

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
    if count not in (2, 7, 30, 365):
        return []

    achievement_id = CONTINUOUS_VISIT_OFFSET + count

    # check if already received achievement
    query = UserAchievement.gql('WHERE owner = :1 AND achievement_id = :2', user.id, achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=user.id, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = CONTINUOUS_VISIT_COUNT_VALUE[count]
    return [{'key': key.id(), 'title': title, 'description': description, 'icon': icon}]
