#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi
import cgitb
from wsgiref import util, simple_server
from wsgiref.validate import validator
cgitb.enable()
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
import bcrypt
from urllib.parse import parse_qsl
import codecs
import sys
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

# データベースファイルのパスを設定
DB_NAME = 'database.db'

class PageManager:
    def __init__(self):
        pass
    
    def __call__(self, env, start_response):
        

    
def db_init():
    # テーブルの作成
    con = sqlite3.connect(DB_NAME)
    con.text_factory = str
    cur = con.cursor()
    create_table = 'create table if not exists users (name text, password text)'
    try:
        cur.execute(create_table)
        print("ok")
    except sqlite3.OperationalError:
        print("er")
        pass

    con.commit()
    cur.close()
    con.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_user(name):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    con.text_factory = str
    con.row_factory = dict_factory
    cur = con.cursor()
    sql = 'select * from users where name = ?'
    res = cur.execute(sql, (name,)).fetchone()
    print(res)

    cur.close()
    con.close()

    return res

def set_user(name, pwd):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    sql = 'insert into users (name, password) values (?,?)'

    try:
        hashed_pwd = hash_pwd(pwd)
        print("hashed_pwd: {}".format(pwd))
        cur.execute(sql, (name, hashed_pwd))
    except Exception as e:
        # print(str(e))
        raise(e)
        return False

    con.commit()
    cur.close()
    con.close()

    return True

def hash_pwd(password, rounds=12):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds)).decode('utf8')


def check_pwd(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf8'), hashed_password.encode('utf8'))


def index(env, error=None):
    request_method = env['REQUEST_METHOD']
    request_path = env['PATH_INFO']

    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    with open('../template/index.html', 'r', encoding='utf-8') as fp:
        html = fp.read()
        html = html.replace('{error}', error if (error is not None) else '')
    
    body = [html.encode('utf-8')]

    return status, headers, body


def home(env, error=None):
    try:
        with open('../template/home.html', 'r', encoding='utf-8') as fp:
            html = fp.read()
            html = html.replace('{error}', error if (error is not None) else '')
        body = [html.encode('utf-8')]
    
    except Exception as e:
        # print(str(e))
        raise(e)
        return internal_server_error(env)

    request_method = env['REQUEST_METHOD']
    request_path = env['PATH_INFO']

    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    body = [html.encode('utf-8')]

    return status, headers, body


def login(env):
    try:
        # フォームデータを取得
        form = cgi.FieldStorage(environ=env,keep_blank_values=True)
        # フォームデータから各フィールド値を取得
        name = form.getvalue("name", "0")
        pwd = form.getvalue("pwd", "0")

        # print("name: {}, pure_pwd: {}".format(name, pwd))

        res = get_user(name)
        print(res)

        if (res is not None):
            if (check_pwd(res["password"], pwd)):
                print("認証成功。")
                # cookie = Cookie.SimpleCookie()
                # if cookie.has_key("session"):
                #     session = cookie["session"].value
                # else:

                #     "session"という名前のクッキーが存在しない時の処理

                return home(env)

            else:
                print("認証失敗。")
                error = "認証失敗。"
                return index(env, error)

        else:
            print("ユーザーが存在しない。新規登録画面へ遷移")
            error = "ユーザーが存在しない。"
            return index(env, error)

    except Exception as e:
        # print(str(e))
        raise(e)
        return internal_server_error(env)

    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    body = [html.encode('utf-8')]

    return status, headers, body

 # POST
def signup(env):
    error = None
    try:
        wsgi_input = env['wsgi.input']
        print(env.get('CONTENT_LENGTH'))
        content_length = int(env.get('CONTENT_LENGTH', 0))
        query = parse_qsl(wsgi_input.read(content_length).decode('UTF-8'))
        print(query)

        # form = cgi.FieldStorage(environ=env,keep_blank_values=True)
        # print(form.keys())
        # print(form)
        # フォームデータから各フィールド値を取得
        # name = form.getvalue("name", "0")
        # pwd = form.getvalue("pwd", "0")
        name = "a"
        pwd = "a"

        # print("name: {}, pure_pwd: {}".format(name, pwd))

        res = get_user(name)
        print(res)

        if (res is not None):
            print("すでにユーザーが存在。ログイン画面へ遷移")
            error = "すでにユーザーが存在。ログイン画面へ遷移"
        else:
            if (set_user(name, pwd)):
                print("ユーザーの作成に成功")

            else:
                print("ユーザーの作成に失敗")
                error = "ユーザーの作成に失敗"

    except Exception as e:
        # print(str(e))
        raise(e)

        return internal_server_error(env)

    return index(env, error)


def not_found(env):
    request_path = env['PATH_INFO']

    status = '404 Not Found'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    body = 'Not Found: {}'.format(request_path)
    body = [body.encode('utf-8')]
    # body = [bytes(line, encoding='utf-8') for line in body.splitlines()]

    return status, headers, body


def internal_server_error(env):
    request_method = env['REQUEST_METHOD']
    request_path = env['PATH_INFO']

    status = '500 INTERNAL SERVER ERROR'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    body = 'Internal Server Error: {} {}'.format(request_method, request_path)
    body = [body.encode('utf-8')]

    return status, headers, body


def bad_request(env):
    request_method = env['REQUEST_METHOD']
    request_path = env['PATH_INFO']

    status = '400 Bad Request'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    body = 'Bad Request: {} {}'.format(request_method, request_path)
    body = [body.encode('utf-8')]

    return status, headers, body


def routing(env):
    request_method = env.get('REQUEST_METHOD')
    request_path = env.get('PATH_INFO')
    query_string = env.get('QUERY_STRING')
    if (query_string == ''):
        query = {}
    else:
        query = dict([q.split('=') for q in query_string.split('&')])
    print(query)

    allowed_request_method = {'GET', 'POST'}

    router = {
        'GET': {
            '/': index,
            '/index': index,
            '/home': home,
            '/login': login,
            '/signup': signup,
        },
        'POST': {
            '/login': login,
            '/signup': signup,
        }
    }

    print(request_method)
    # GET, POST以外は404
    if request_method not in allowed_request_method:
        return bad_request(env)

    # try:
    #     print(request_path)
    #     # if ('?' in post_url):
    #     #     path, query_string = post_url.split('?')
    #     #     print(path, query_string)
    #     #     query = dict([q.split('=') for q in query_string.split('&')])
    #     # else:
    #     #     path, query = post_url, {}
        
    #     # print(path)
    #     # print(query)
    # except IndexError:
    #     path = ''
    #     query = {}
    
    return router[request_method].get(request_path, not_found)(env)


@validator
def app(environ,start_response):
    status, headers, body = routing(environ)

    # status, headers, body = routing(environ)
    start_response(status, headers)
    return body


# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, app)
    server.serve_forever()
    db_init()
    print("start")
