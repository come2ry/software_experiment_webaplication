#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
import logging
from http import cookies
import os
from functions import get_user, set_user, check_pwd, db_init
from config import DB_NAME
from urllib.parse import parse_qsl
from wsgiref import util, simple_server
from wsgiref.validate import validator
cgitb.enable()


class PageManager:

    def __init__(self):
        self.router =  {
            'GET': {
                '/': self.index,
                '/index': self.index,
                '/home': self.home,
            },
            'POST': {
                '/': self.index,
                '/login': self.login,
                '/signup': self.signup,
            }
        }

    # @validator
    def __call__(self, env, start_response):
        status, headers, body = self.routing(env, start_response)

        start_response(status, headers)
        return body


    def routing(self, env, start_response):  # routing
        request_method = env.get('REQUEST_METHOD')
        request_path = env.get('PATH_INFO')
        cookie = cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
        print('cookie: ', end='')
        print(cookie)

        if (request_method == 'GET'):
            params = cgi.FieldStorage(environ=env, keep_blank_values=True)
            params = dict([(key, params[key].value) for key in params.keys()])
            print('GET', end=": ")
            print(params)
            # query_string = env.get('QUERY_STRING')
            # if (query_string == ''):
            #    query = {}
            # else:
            #     query = dict([q.split('=') for q in query_string.split('&')])
            # print(query)

        elif (request_method == 'POST'):
            wsgi_input = env['wsgi.input']
            content_length = int(env.get('CONTENT_LENGTH', 0))
            params = dict(parse_qsl(wsgi_input.read(content_length).decode('UTF-8')))
            print('POST', end=": ")
            print(params)

        allowed_request_method = {'GET', 'POST'}

        print(request_method)
        # GET, POST以外は404
        if request_method not in allowed_request_method:
            return self.bad_request(env, params)
        
        return self.router[request_method].get(request_path, self.not_found)(env, params=params, error=None)



    def index(self, env, params={}, error=None):
        try:
            with open('../template/index.html', 'r', encoding='utf-8') as fp:
                html = fp.read()
                html = html.replace('{error}', error if (error is not None) else '')
            body = [html.encode('utf-8')]
        
        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)


        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        body = [html.encode('utf-8')]

        return status, headers, body


    def home(self, env, params={}, error=None):
        try:
            with open('../template/home.html', 'r', encoding='utf-8') as fp:
                html = fp.read()
                html = html.replace('{error}', error if (error is not None) else '')
            body = [html.encode('utf-8')]
        
        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        body = [html.encode('utf-8')]

        return status, headers, body


    def login(self, env, params={}, error=None):
        cookie = cookies.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
        try:
            name = params.get('name', 'guest')
            pwd = params.get('password', 'guest')
            params = {}

            res = get_user(name)
            print('login_user: ', end="")
            print(res)

            if (res is not None):
                if (check_pwd(res["password"], pwd)):
                    print("認証成功")
                    error = "<font color='blue'>ログイン成功</font>"
                    # cookie = Cookie.SimpleCookie()
                    # if cookie.has_key("session"):
                    #     session = cookie["session"].value
                    # else:

                    #     "session"という名前のクッキーが存在しない時の処理

                    home_url = util.application_uri(env)
                    cookie['error'] = error.encode('utf-8')
                    
                    status = '303 See Other'
                    headers = [('Content-type', 'text/html'), ('Location', home_url+'home'), ('Set-Cookie', cookie["error"].OutputString())]
                    body = ["<p>リダイレクト中</p>".encode('utf-8')]
                    return status, headers, body

                else:
                    print("認証失敗")
                    error = "<font color='red'>認証失敗</font>"


            else:
                print("ユーザーが存在しない。新規登録画面へ遷移")
                error = "<font color='red'>ユーザーが存在しない</font>"


            home_url = util.application_uri(env)
            cookie['error'] = error.encode('utf-8')
            
            status = '303 See Other'
            headers = [('Content-type', 'text/html'), ('Location', home_url), ('Set-Cookie', cookie["error"].OutputString())]
            body = ["<p>リダイレクト中</p>".encode('utf-8')]

        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        home_url = util.application_uri(env)
        
        status = '303 See Other'
        headers = [('Content-type', 'text/html'), ('Location', home_url)]
        body = ["<p>リダイレクト中...</p>".encode('utf-8')]

        return status, headers, body

    # POST
    def signup(self, env, params={}, error=None):
        cookie = cookies.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
        try:
            name = params.get('name', 'guest')
            pwd = params.get('password', 'guest')
            params = {}
            # print("name: {}, pure_pwd: {}".format(name, pwd))

            res = get_user(name)
            print('signup_user: ', end="")
            print(res)

            if (res is not None):
                print("すでにユーザーが存在\nログイン画面へ遷移")
                error = "<font color='red'>すでにユーザーが存在\nログイン画面へ遷移</font>"
            else:
                if (set_user(name, pwd)):
                    print("ユーザーの作成に成功")
                    error = "<font color='blue'>ユーザー作成完了</font>"

                else:
                    print("ユーザーの作成に失敗")
                    error = "<font color='red'>ユーザーの作成に失敗</font>"

        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        home_url = util.application_uri(env)
        cookie['error'] = error.encode('utf-8')
        
        status = '303 See Other'
        headers = [('Content-type', 'text/html'), ('Location', home_url), ('Set-Cookie', cookie["error"].OutputString())]
        body = ["<p>リダイレクト中</p>".encode('utf-8')]

        return status, headers, body


    def not_found(self, env, params={}, error=None):
        request_path = env['PATH_INFO']

        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Not Found: {}'.format(request_path)
        body = [body.encode('utf-8')]

        return status, headers, body


    def internal_server_error(self, env, params={}, error=None):
        request_method = env['REQUEST_METHOD']
        request_path = env['PATH_INFO']

        status = '500 INTERNAL SERVER ERROR'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Internal Server Error: {} {}'.format(request_method, request_path)
        body = [body.encode('utf-8')]

        return status, headers, body


    def bad_request(self, env, params={}, error=None):
        request_method = env['REQUEST_METHOD']
        request_path = env['PATH_INFO']

        status = '400 Bad Request'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Bad Request: {} {}'.format(request_method, request_path)
        body = [body.encode('utf-8')]

        return status, headers, body



# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    db_init()
    page_manager = PageManager()
    server = simple_server.make_server('', 8080, page_manager)
    server.serve_forever()
    print("start")


# start_response('303 See Other', [('Content-type', 'text/plain'),
#             ('Location', util.request_uri(environ))])