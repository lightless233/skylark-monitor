#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    searcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    由于搜素 API 没有排序功能，且我们只需要最近更新的数据
    需要请求到所有的内容，然后对结果按照更新时间进行排序，然后再获取最新更新的 doc 数据
    排序方案有两种：
      1. 使用 DB 排序，创建一个表，rule_id, doc_id, update_time，每次搜素完成后，将对应规则 ID 的数据进行排序
      2. 使用 redis 排序，使用 sorted set，分数为时间戳，值为 doc id，每个规则创建一个新的 set
    使用 DB 可以复用数据，但是要一条一条检查更新时间是否发生变更
    使用 redis 不能复用历史数据，但是可以直接内存排序

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
import json
import threading
import time
import traceback
import typing

import requests
from silex.engines import MultiThreadEngine

from skylark.constant import QueuesName, SearchMsg
from skylark.database.models.token import SkylarkTokenModel
from skylark.utils.commons import CommonsUtil
from skylark.utils.logger import LoggerFactory
from skylark.utils.task_queue import TaskQueue, RawRedis


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

    def build_request_params(self, keyword, page):
        return {
            "type": "doc",
            "q": self._encode_rule(keyword),
            "offset": page,
        }

    @staticmethod
    def get_valid_token():
        return SkylarkTokenModel.objects.get_available_token()

    def do_request(self, keyword, page) -> typing.Optional[dict]:
        """
        发起搜素请求，每次请求一页，请求第几页由 page 参数控制
        :param keyword:
        :param page:
        :return:
        """

        # 构建请求参数
        params = self.build_request_params(keyword, page)
        self.logger.debug(f"request params: {params}")

        retry = 3
        while retry and self.is_running_status():
            retry -= 1

            # 随机选取一个代理设置，如果设置不使用代理，则返回空字典
            proxies = CommonsUtil.get_random_proxy()

            # 获取一个 token
            token = self.get_valid_token()
            headers = {
                "x-auth-token": token
            }

            try:
                response = requests.get(self.SEARCH_API, params=params, headers=headers, timeout=9, proxies=proxies)
                return response.json()
            except requests.RequestException as e:
                self.logger.error(
                    "Error while request to search api. error: {}, traceback: {}".format(e, traceback.format_exc()))
        else:
            # 已达到最大请求次数
            self.logger.warning(f"request max retry times exceeded. {keyword=}")
            return None

    @staticmethod
    def conv(t):
        return int(time.mktime(time.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")))

    def parse_doc_meta(self, response: dict) -> list:
        data = response.get("data")
        if not data:
            return []
        return [{it.get("id"): self.conv(it.get("target").get("content_updated_at"))} for it in data]

    def sort_docs(self, docs_meta: list):
        """
        对搜素到的结果按照更新时间进行排序
        先采用 redis 的方案，每次排序完成后删除 redis 中的集合
        :param docs_meta:
        :return:
        """
        # 1. 生成一个集合名称用于排序
        set_name = f"{self.local.current_name}_{CommonsUtil.get_random_string()}"

        # 2. 连接 redis
        r = RawRedis.get_raw_redis()

        # 3. 把待排序的东西扔进去
        for item in docs_meta:
            r.zadd(set_name, item)

        # 4. 获取排序后的数据，取最新的 30 个数据
        docs_id_list = r.zrevrange(set_name, 0, 29)

        return docs_id_list

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

            # 调用搜素 API
            docs_meta_list = []
            page = 1
            while self.is_running_status():
                self.logger.debug(f"trying to request page {page}")
                response = self.do_request(message.content, page)
                page += 1
                if response is None:
                    continue
                if not int(response.get('meta').get("total")):
                    break

                docs_meta_list.extend(self.parse_doc_meta(response))

            self.logger.debug(f"docs_meta_list size: {len(docs_meta_list)}")
            self.sort_docs(docs_meta_list)

            # TODO：添加任务到下一个引擎中

        self.logger.info(f"{current_name} end.")
