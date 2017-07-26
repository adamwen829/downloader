#!/usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.web

from app.urls import handlers
from app.config import APPLICATION_CONF


def get_application():
    application = tornado.web.Application(handlers, **APPLICATION_CONF)
    return application


def main():
    application = get_application()
    application.listen(3001)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
