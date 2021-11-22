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

from django.conf import settings


class CommonsUtil:

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
