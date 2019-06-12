#! /usr/bin/env python3
# -*- coding: utf-8 -*-
####### @tanaka #######

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

import sys
sys.path.append("/var/www/cgi-bin")

from app import app


def application(env, start_response):
    return app(env, start_response)


if __name__ == '__main__':
    from wsgiref import simple_server
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()