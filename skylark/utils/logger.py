#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    skylark.utils.logger
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import logging
import logging.handlers
import os

from django.conf import settings


class LoggerFactory:
    LOG_FMT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def get_logger(cls, name=None, level="DEBUG"):
        _logger = logging.getLogger(name if name is not None else __name__)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(
            logging.Formatter(fmt=cls.LOG_FMT, datefmt=cls.DATE_FMT)
        )
        _logger.addHandler(stdout_handler)

        if settings.LOG_TO_FILE:
            if not os.path.exists(settings.LOG_PATH):
                os.mkdir(settings.LOG_PATH)
            log_filename = os.path.join(settings.LOG_PATH, settings.LOG_FILENAME)
            file_handler = logging.handlers.TimedRotatingFileHandler(log_filename, when="midnight", backupCount=7)
            file_handler.setFormatter(
                logging.Formatter(fmt=cls.LOG_FMT, datefmt=cls.DATE_FMT)
            )
            _logger.addHandler(file_handler)

        _logger.setLevel(level)
        return _logger


logger = LoggerFactory.get_logger("global")
