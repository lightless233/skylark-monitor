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
import traceback

import requests
from silex.engines import MultiThreadEngine

from skylark.constant import QueuesName, SearchMsg
from skylark.utils.commons import CommonsUtil
from skylark.utils.logger import LoggerFactory
from skylark.utils.task_queue import TaskQueue


class SearcherEngine(MultiThreadEngine):
    logger = LoggerFactory.get_logger(__name__)

    SEARCH_API = "https://www.yuque.com/api/v2/search"

    def __init__(self):
        super(SearcherEngine, self).__init__("SearcherEngine")

        self.local = threading.local()

    def get_message(self):
        message = self.local.search_queue.get_message()
        return message[1] if message else None

    def parse_search_message(self, message):
        try:
            msg: SearchMsg = SearchMsg.from_str(message)
        except json.JSONDecodeError:
            self.logger.warning("{} Receive invalid message: {}".format(self.local.current_name, message))
            return None
        except ValueError as e:
            self.logger.warning(f"msg value error: {message=}, error: {e}")
            return None

        return msg

    def connect_queue(self):
        """
        连接到 redis 队列，返回两个队列对象
        分别是 search_queue 和 save_queue
        同时也会存储在 local 变量中
        :return:
        """
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

    def build_request_params(self, keyword):
        return {
            "tab": "public",
            "scope": "/",
            "type": "content",
            "q": self._encode_rule(keyword)
        }

    def do_request(self, params):
        """
        发起搜素请求
        :param params:
        :return:
        """
        retry = 3
        while retry and self.is_running_status():
            retry -= 1

            # 随机选取一个代理设置，如果设置不使用代理，则返回空字典
            proxies = CommonsUtil.get_random_proxy()

            # 获取一个 token
            cookies = self.get_valid_cookie()

            try:
                response = requests.get(self.SEARCH_API, params=params, cookies=cookies, timeout=9, proxies=proxies)
                return response.json()
            except requests.RequestException as e:
                self.logger.error(
                    "Error while request to search api. error: {}, traceback: {}".format(e, traceback.format_exc()))
        else:
            # 已达到最大请求次数
            pass

    def _worker(self):
        self.local.current_name = current_name = threading.current_thread().name
        self.logger.info(f"{current_name} start.")

        # 连接到 redis 队列
        self.connect_queue()

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

            # 对搜素词进行编码
            encoded_keyword = self._encode_rule(rule_content)
            self.logger.debug("rule_content: {}, after encode: {}".format(rule_content, encoded_keyword))

            self.do_request(rule_content)

        self.logger.info(f"{current_name} end.")
