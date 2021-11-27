#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import random

from django.db import models

from ._base import BaseModel


class SkylarkTokenManager(models.Manager):

    def get_available_token(self) -> "SkylarkTokenModel":
        rows = self.filter(is_deleted=0, status=1, rest_count__gt=0).all()
        return random.choice(rows)


class SkylarkTokenModel(BaseModel):
    class Meta:
        db_table = "skylark_token"

    name = models.CharField(max_length=64, default="")
    token = models.CharField(max_length=64, default="")

    # 状态
    # 1：启用，0：关闭
    status = models.PositiveSmallIntegerField(default=1)

    # 该 token 的剩余可用次数
    rest_count = models.PositiveIntegerField(default=0)

    objects = SkylarkTokenManager()
