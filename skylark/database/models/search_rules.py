#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    skylark.database.models.search_rules
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    搜索规则

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
from django.db import models

from ._base import BaseModel


class SkylarkSearchRulesManager(models.Manager):
    pass


class SkylarkSearchRulesModel(BaseModel):
    class Meta:
        db_table = "skylark_search_rules"

    rule_name = models.CharField(max_length=64, default="")
    content = models.TextField(default="")

    # 1 - 启用
    # 2 - 关闭
    status = models.PositiveSmallIntegerField(default=1)

    # 上次搜索时间
    last_search_time = models.DateTimeField(auto_now_add=True)

    # 搜索间隔，默认15分钟搜索一次
    interval = models.PositiveIntegerField(default=15)

    # 额外信息，json格式存储
    ext_info = models.TextField(default="{}")

    # 不需要默认的 Manager 行为了，感觉用不到
    # 用到了再说
    objects = SkylarkSearchRulesManager()
