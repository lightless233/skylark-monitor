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

from django.conf import settings

# noinspection PyPackageRequirements
from silex.redis_queue import RedisQueue


class TaskQueue:

    @classmethod
    def get_queue(cls, queue_name):
        return RedisQueue(
            settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_PASSWORD, settings.REDIS_DB_INDEX, queue_name
        ).connect()
