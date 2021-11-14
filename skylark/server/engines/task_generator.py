#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    skylark.server.engines.task_generator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    任务生成器，负责生产监控任务

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
# noinspection PyPackageRequirements
from silex.engines import SingleThreadEngine

from skylark.constant import QueuesName
from skylark.utils.logger import LoggerFactory
from skylark.utils.task_queue import TaskQueue


class TaskGenerator(SingleThreadEngine):
    logger = LoggerFactory.get_logger(__name__)

    def __init__(self):
        super(TaskGenerator, self).__init__("TaskGenerator")

    def _worker(self):
        self.logger.info(f"{self.name} start.")

        # 连接到消息队列
        search_queue = TaskQueue.get_queue(QueuesName.SEARCH_QUEUE)
        if not search_queue:
            self.logger.error("Can't connect to queue.")
            exit(-1)

        # 主循环
        while self.is_running_status():
            pass

        self.logger.info(f"{self.name} stop.")
