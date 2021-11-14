#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    skylark
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    $END$

    :author:    lightless <root@lightless.me>
    :homepage:  None
    :license:   GPL-3.0, see LICENSE for more details.
    :copyright: Copyright (c) 2017-2021 lightless. All rights reserved
"""
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Start the SkylarkMon application."

    valid_start_mode = ["server", "agent", "all"]

    def add_arguments(self, parser):
        parser.add_argument("--mode", action="store", dest="start_mode", help="SkylarkMon start mode.")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("starting SkylarkMon application."))
        self.stdout.write(self.style.SUCCESS("start mode: {}".format(options.get("start_mode"))))

        # 检查参数是否合法
        start_mode = options.get("start_mode")
        if start_mode not in self.valid_start_mode:
            self.stdout.write(self.style.ERROR("start mode error. Only can be one of {}".format(self.valid_start_mode)))
            exit(-1)

        try:
            if start_mode == "server" or start_mode == "all":
                # 启动 server app
                pass

            if start_mode == "agent" or start_mode == "all":
                # 启动 agent app
                pass
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error while running application, error: {}".format(e)))
            self.stdout.write(self.style.ERROR("Full stack trace:"))
            import sys
            import traceback

            tb = "".join(traceback.TracebackException(*sys.exc_info()).format())
            self.stdout.write(self.style.ERROR(tb))
