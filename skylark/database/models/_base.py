#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    skylark.database.models._base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    数据库模型的基类

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""

from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_time = models.DateTimeField(auto_now=True)
    updated_time = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
