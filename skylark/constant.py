#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    constant
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import json
import types


class GlobalVars:
    pass


class QueuesName:
    SEARCH_QUEUE = "skylark_mon_search_queue"
    SAVE_QUEUE = "skylark_mon_save_queue"


class BaseMsg:
    _available_fields = []

    @classmethod
    def _fields(cls):
        if not cls._available_fields:
            cls._available_fields = [
                k for k, v in cls.__dict__.items() if
                not k.startswith("_") and not isinstance(v, types.FunctionType) and not isinstance(v, classmethod)
            ]

        return cls._available_fields

    def to_dict(self):
        return self.__dict__

    def to_str(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_dict(cls, value: dict):
        msg = cls()
        value_keys = value.keys()
        fields = cls._fields()
        for _f in fields:
            if _f not in value_keys:
                raise ValueError(f"missing '{_f}' on parameters.")
            msg.__dict__[_f] = value.get(_f)
        return msg

    @classmethod
    def from_str(cls, value: str):
        return cls.from_dict(json.loads(value))


class SearchMsg(BaseMsg):
    rule_id: int = 0
    content: str = ""
    token: str = ""
    token_id: int = 0
