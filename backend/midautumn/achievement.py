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
from midautumn.utils import pretty_time


ITEM_OFFSET = 1000
ITEM_COUNT_OFFSET = 2000
TIME_OFFSET = 3000
LIKE_COUNT_OFFSET = 4000
COMMENT_COUNT_OFFSET = 5000
CONTINUOUS_VISIT_OFFSET = 6000
MISC_OFFSET = 7000
LAST_OFFSET = 8000

ITEM_KEY = [u'玉米', u'臭豆腐', u'可樂', u'流星下的怨', u'星光戰士舞',
            u'Cloony 是大帥哥', u'草莓', u'蝦子', u'西瓜', u'仙女棒',
            u'打火機', u'假假課', ]
ITEM_VALUE = {
    u'玉米': (u'Ron 的最愛。', 'corn.png'),
    u'臭豆腐': (u'臭豆腐怎麼烤啊？', 'stinky-tofu.png'),
    u'可樂': (u'俊輝的最愛。', 'coke.png'),
    u'流星下的怨': (u'Cloony 和 San 的經典。', 'meteor.png'),
    u'星光戰士舞': (u'Leo 的代表作。', 'starlight-warrior.png'),
    u'Cloony 是大帥哥': (u'圖示說明了一切。', 'cloony-toro.png'),
    u'草莓': (u'跟阿撥沒有關係，純粹她照片太多。', 'strawberry.png'),
    u'蝦子': (u'蝦子交給 Leo 串最快。', 'shrimp.png'),
    u'西瓜': (u'跟阿撥沒有關係，純粹她照片太多。', 'watermelon.png'),
    u'仙女棒': (u'阿伯與仙女棒。', 'sparkler.png'),
    u'打火機': (u'或是找卡姐也可以。', 'lighter.png'),
    u'假假課': (u'小寶的核心團隊。', 'section-fake.png'),
    }

ITEM_COUNT_VALUE = {
    1: (u'頭香', u'頭香不必搶，有提議就有保庇。', 'item-count-1.png'),
    5: (u'幕後推手', u'就是需要你這種人！再多推薦一點！', 'item-count-5.png'),
    10: (u'第十個物品', u'恭喜你推薦了你的第十個物品。', 'item-count-10.png'),
    50: (u'第五十個物品', u'太誇張了！你推薦了你的第五十個物品。', 'item-count-50.png'),
    100: (u'第一百個物品', u'你贏了！你推薦了你的第一百個物品。', 'item-count-100.png'),
    300: (u'這就是斯巴達！（物品）', u'這就是斯巴達！你推薦了你的第三百個物品。', 'item-count-300.png'),
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
    1: (u'應聲蟲', u'食指點一下就可以附和別人，過太爽。', 'like-count-1.png'),
    5: (u'人云亦云', u'人家說什麼你就跟著說好！', 'like-count-5.png'),
    10: (u'拾人牙慧', u'不必動腦很開心。', 'like-count-10.png'),
    50: (u'攀龍附鳳', u'別人說的都是好的，總是要推一下。', 'like-count-50.png'),
    100: (u'百發百中', u'恭喜你按了一百次「讚」。', 'like-count-100.png'),
    300: (u'這就是斯巴達！（讚）', u'這就是斯巴達！送出了第三百個讚。', 'like-count-300.png'),
}

COMMENT_COUNT_VALUE = {
    1: (u'第一個留言', u'送出了第一個留言。', 'comment-count-1.png'),
    5: (u'第五個留言', u'送出了第五個留言。', 'comment-count-5.png'),
    10: (u'第十個留言', u'送出了第十個留言。', 'comment-count-10.png'),
    50: (u'第五十個留言', u'太誇張了！送出了第五十個留言。', 'comment-count-50.png'),
    100: (u'第一百個留言', u'你贏了！送出了第一百個留言。', 'comment-count-100.png'),
    300: (u'這就是斯巴達！（留言）', u'這就是斯巴達！送出了第三百個留言。', 'comment-count-300.png'),
}

CONTINUOUS_VISIT_VALUE = {
    2: (u'回鍋', u'人客～您昨天也有來ㄟ！', 'continuous-visit-count-2.png'),
    7: (u'連續一週', u'週末假日也上班，薪資加倍。', 'continuous-visit-count-7.png'),
    30: (u'滿月', u'上班都沒這麼勤快...。', 'continuous-visit-count-30.png'),
    365: (u'全年無休', u'......你一定有在用外掛！', 'continuous-visit-count-365.png'),
}

LIKE_REMOVED_ACHIEVEMENT_ID = MISC_OFFSET + 1
LIKE_REMOVED_ACHIEVEMENT_VALUE = (u'太狠心了', u'太狠心了，竟然將讚取消！', 'like-removed.png')
COMMENT_REMOVED_ACHIEVEMENT_ID = MISC_OFFSET + 2
COMMENT_REMOVED_ACHIEVEMENT_VALUE = (u'刪除留言', u'刪除留言。@@', 'comment-removed.png')


class UserAchievement(db.Model):
    owner = db.ReferenceProperty(FacebookUser, collection_name='achievement_set', required=True)
    achievement_id = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @property
    def info(self):
        aid = self.achievement_id
        title, description, icon = None, None, None

        if aid == LIKE_REMOVED_ACHIEVEMENT_ID:
            title, description, icon = LIKE_REMOVED_ACHIEVEMENT_VALUE
        elif aid == COMMENT_REMOVED_ACHIEVEMENT_ID:
            title, description, icon = COMMENT_REMOVED_ACHIEVEMENT_VALUE
        elif aid >= LAST_OFFSET:
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
        relative_url = '/achievement/%s' % self.key().id()
        result = {'created': pretty_time(self.created),
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


def _check_like_count(edge):
    owner = edge.owner

    query = owner.edge_set.filter('created =', True)
    count = query.count()

    if count not in LIKE_COUNT_VALUE:
        return []

    achievement_id = LIKE_COUNT_OFFSET + count

    # check if already received achievement
    query = owner.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = LIKE_COUNT_VALUE[count]
    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]

def _check_like_removed(edge):
    owner = edge.owner

    query = owner.edge_set.filter('removed =', True)

    if query.count() <= 0:
        return []

    achievement_id = LIKE_REMOVED_ACHIEVEMENT_ID

    # check if already received achievement
    query = owner.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    title, description, icon = LIKE_REMOVED_ACHIEVEMENT_VALUE
    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]

def check_like(edge):
    achievements = []
    achievements.extend(_check_like_count(edge))
    achievements.extend(_check_like_removed(edge))
    return achievements


def check_comment(comment=None, owner=None):
    if not owner and comment:
        owner = comment.owner

    if not owner:
        return []

    achievement_id = None
    title, description, icon = None, None, None

    if not comment:
        achievement_id = COMMENT_REMOVED_ACHIEVEMENT_ID
    else:
        count = owner.comment_set.count()

        if count not in COMMENT_COUNT_VALUE:
            return []

        achievement_id = COMMENT_COUNT_OFFSET + count

    # check if already received achievement
    query = owner.achievement_set.filter('achievement_id =', achievement_id)
    if query.count() > 0:
        return []

    ua = UserAchievement(owner=owner, achievement_id=achievement_id)
    key = ua.put()

    if not comment:
        title, description, icon = COMMENT_REMOVED_ACHIEVEMENT_VALUE
    else:
        title, description, icon = COMMENT_COUNT_VALUE[count]

    return [{'key': key.id(),
             'title': title,
             'description': description,
             'icon_url': '/img/' + icon,
             }]


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
