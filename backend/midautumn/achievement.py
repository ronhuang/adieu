#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Midautumn
# Copyright 2011 Ron Huang
# See LICENSE for details.


from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
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


ITEM_KEY = ['玉米', '臭豆腐', '可樂', '流星下的怨', '星光戰士舞', 'Cloony 是大帥哥', ]
ITEM_VALUE = {
    '玉米': ('Ron 的最愛。', 'corn.png'),
    '臭豆腐': ('臭豆腐怎麼烤啊？', 'stinky-tofu.png'),
    '可樂': ('俊輝的最愛。', 'coke.png'),
    '流星下的怨': ('Cloony 和 San 的經典。', 'meteor.png'),
    '星光戰士舞': ('Leo 的代表作。', 'starlight-warrior.png'),
    'Cloony 是大帥哥': ('...', 'cloony-toro.png'),
    }

ITEM_COUNT_VALUE = {
    1: ('恭喜你推薦了你的第一個物品。', 'item-count-1.png'),
    5: ('恭喜你推薦了你的第五個物品。', 'item-count-5.png'),
    10: ('恭喜你推薦了你的第十個物品。', 'item-count-10.png'),
    50: ('太誇張了！你推薦了你的第五十個物品。', 'item-count-50.png'),
    100: ('你贏了！你推薦了你的第一百個物品。', 'item-count-100.png'),
    500: ('真有毅力！你推薦了你的第五百個物品。', 'item-count-500.png'),
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
    return [{'key': key.id(), 'achievement_id': achievement_id, 'description': description, 'icon': icon}]

def _check_item_count(obj):
    owner = obj.owner

    query = MidautumnObject.gql('WHERE owner = :1', owner)
    count = query.count()

    if count not in (1, 5, 10, 50, 100, 500):
        return []

    achievement_id = ITEM_COUNT_OFFSET + count
    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    description, icon = ITEM_COUNT_VALUE[count]
    return [{'key': key.id(), 'achievement_id': achievement_id, 'description': description, 'icon': icon}]

def check_post(obj):
    achievements = []
    achievements.extend(_check_item(obj))
    achievements.extend(_check_item_count(obj))
    return achievements


def check_like():
    pass


def check_comment():
    pass
