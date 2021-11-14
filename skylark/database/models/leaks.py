#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    leaks
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
from django.db import models

from skylark.database.models._base import BaseModel


class SkylarkLeaksManager(models.Manager):
    pass


class SkylarkLeaksModel(BaseModel):
    class Meta:
        db_table = "skylark_leaks"

    # 文章标题
    title = models.CharField(max_length=256, default="NoTitle")

    # 文章的原始链接
    raw_url = models.CharField(max_length=1024, default="")

    # 搜素到的文章的跳转链接
    # 里面的 ID 大概可以用来去重
    go_url = models.CharField(max_length=1024, default="")

    # 知识库名称
    book_name = models.CharField(max_length=256, default="")

    # 知识库所属的 group 名称
    group_name = models.CharField(max_length=256, default="")

    # 文章摘要信息
    abstract = models.TextField(default="")

    # search_rule_id
    search_rule_id = models.PositiveBigIntegerField(default=0)

    # 这条泄露信息的状态
    # 1 - 待处理，2 - 确认是泄露，3-误报
    status = models.PositiveSmallIntegerField(default=1)

    # 文章的几个时间值
    content_updated_at = models.DateTimeField()
    first_published_at = models.DateTimeField()
    published_at = models.DateTimeField()
    paper_created_at = models.DateTimeField()
    paper_updated_at = models.DateTimeField()

    # 额外数据
    ext_info = models.TextField(default="{}")

    objects = SkylarkLeaksManager()
