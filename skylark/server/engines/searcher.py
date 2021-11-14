#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    searcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import json
import threading

from silex.engines import MultiThreadEngine

from skylark.constant import QueuesName
from skylark.utils.logger import LoggerFactory
from skylark.utils.task_queue import TaskQueue


class SearcherEngine(MultiThreadEngine):
    logger = LoggerFactory.get_logger(__name__)

    def __init__(self):
        super(SearcherEngine, self).__init__("SearcherEngine")

        self.local = threading.local()

    def get_message(self):
        message = self.local.search_queue.get_message()
        return message[1] if message else None

    def parse_search_message(self, message):
        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            self.logger.warning("{} Receive invalid message: {}".format(self.local.current_name, message))
            return None

        rule_id = msg.get("rule_id")
        rule_content = msg.get("content")
        if not rule_id or not rule_content:
            self.logger.warning(
                "{} Receive invalid message: {}, missing field.".format(self.local.current_name, message)
            )
            return None

        return msg

    def connect_queue(self):
        try:
            search_queue = TaskQueue.get_queue(QueuesName.SEARCH_QUEUE)
            save_queue = TaskQueue.get_queue(QueuesName.SAVE_QUEUE)
            if not search_queue or not save_queue:
                self.logger.error("Connect to redis failed.")
                return

            self.local.search_queue = search_queue
            self.local.save_queue = save_queue
            return search_queue, save_queue

        except Exception as e:
            self.logger.error("Exception while connecting to redis, error: {}".format(e))
            return

    @staticmethod
    def _encode_rule(rule_content):
        keyword_list = rule_content.split(" ")
        escaped_keyword_list = list(map(lambda x: x.encode("unicode_escape").decode("utf8"), keyword_list))
        return "+".join(escaped_keyword_list)

    def _worker(self):
        self.local.current_name = current_name = threading.current_thread().name
        self.logger.info(f"{current_name} start.")

        # 连接到 redis 队列
        search_queue, save_queue = self.connect_queue()

        # 主循环
        while self.is_running_status():
            raw_message = self.get_message()
            if not raw_message:
                self.ev.wait(1)
                continue
            message = self.parse_search_message(raw_message)
            if not message:
                self.ev.wait(1)
                continue

            rule_id = message["rule_id"]
            rule_content = message["rule_content"]

        self.logger.info(f"{current_name} end.")
