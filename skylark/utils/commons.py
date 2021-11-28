#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    commons
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    一些通用的工具

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import random
import string

from django.conf import settings


class CommonsUtil:
    char_pool = string.ascii_letters + string.digits

    @classmethod
    def get_random_proxy(cls) -> dict[str, str]:
        """
        随机选取一个代理设置
        :return:
        """
        if settings.USE_PROXY:
            if len(settings.PROXIES_LIST) == 1:
                return settings.PROXIES_LIST[0]
            else:
                return random.choice(settings.PROXIES_LIST)
        else:
            return {}

    @classmethod
    def get_random_string(cls, length=6):
        """
        生成随机字符串
        :param length:
        :return:
        """
        return random.sample(cls.char_pool, length)
