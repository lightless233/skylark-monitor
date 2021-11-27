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
import datetime

from silex.engines import SingleThreadEngine

from skylark.constant import QueuesName, SearchMsg
from skylark.database.models import SkylarkSearchRulesModel
from skylark.database.models.token import SkylarkTokenModel
from skylark.utils.logger import LoggerFactory
from skylark.utils.task_queue import TaskQueue


class TaskGenerator(SingleThreadEngine):
    logger = LoggerFactory.get_logger(__name__)

    def __init__(self):
        super(TaskGenerator, self).__init__("TaskGenerator")

    def _worker(self):
        self.logger.info(f"{self.name} start.")

        # 连接到消息队列
        try:
            search_queue = TaskQueue.get_queue(QueuesName.SEARCH_QUEUE)
            if not search_queue:
                self.logger.error("Can't connect to queue.")
                return
        except Exception as e:
            self.logger.error("Exception while connect to redis. Error: {}".format(e))
            return

        # 主循环
        while self.is_running_status():

            # 每隔 30 秒检查一次所有的规则刷新时间
            self.ev.wait(30)

            all_rules = SkylarkSearchRulesModel.objects.get_all_enabled_rules()
            for _rule in all_rules:
                if _rule.last_search_time + datetime.timedelta(minutes=_rule.interval) < datetime.datetime.now():
                    # 该刷新了

                    msg = SearchMsg()
                    msg.rule_id = _rule.id
                    msg.content = _rule.content

                    # 获取一个 token 一同给 searcher
                    token_row = SkylarkTokenModel.objects.get_available_token()
                    msg.token_id = token_row.id
                    msg.token = token_row.token

                    self.logger.debug("put rule to queue, id: {}, content: {}".format(_rule.id, _rule.content))
                    search_queue.put_message(msg.to_str())

        self.logger.info(f"{self.name} stop.")
