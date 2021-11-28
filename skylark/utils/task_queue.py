#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    queue
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import redis
from django.conf import settings
from silex.redis_manager import RedisQueue, RedisManager


class TaskQueue:

    @classmethod
    def get_queue(cls, queue_name):
        _queue = RedisQueue(
            settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD, settings.REDIS_DB_INDEX, queue_name
        )
        if _queue.connect():
            return _queue
        else:
            raise ConnectionError("Connect redis failed.")


class RawRedis:
    @staticmethod
    def get_raw_redis() -> redis.Redis:
        r = RedisManager(
            settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD, settings.REDIS_DB_INDEX
        )
        if r.connect():
            return r.get_redis_connection()
        else:
            raise ConnectionError("Connect redis failed.")
