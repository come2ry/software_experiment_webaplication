#! /usr/bin/env python3
# -*- coding: utf-8 -*-
####### @tanaka #######

# CGIモジュールをインポート
import cgi
import cgitb
import copy
import json
import logging
import random
# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3
import string
import sys
from http import cookies
from urllib.parse import parse_qsl
from wsgiref import simple_server, util
from wsgiref.validate import validator

sys.path.append("/var/www/cgi-bin")

from config import DB_NAME, GAME_CONFIG
from functions import (check_pwd, db_init, game_log, get_user, set_cookie,
                       set_user, set_user_session, update_user_points)

cgitb.enable()



class PageManager:
    def __init__(self):
        self.router =  {
            'GET': {
                '/': self.index,
                '/index': self.index,
                '/home': self.home,
                '/home/game': self.game,
                '/logout': self.logout,
                '/static/css/style.css': self.get_statics,
                '/static/css/chat-style.css': self.get_statics,
                '/static/bootstrap/css/bootstrap.min.css': self.get_statics,
                '/static/js/jquery.pwdMeasure.min.js': self.get_statics,
                '/static/js/script.js': self.get_statics,
            },
            'POST': {
                '/': self.index,
                '/login': self.login,
                '/logout': self.logout,
                '/signup': self.signup,
                '/home/game': self.game,
            }
        }
        
        self.user_id = None
        self.session_id = None
        self.sessions = {}
        self.error = None
        self.font_color = None

    # @validator
    def __call__(self, env, start_response):
        status, headers, body = self.routing(env, start_response)

        start_response(status, headers)
        return body
    
    def init_session(self, env):
        cookie = cookies.SimpleCookie()
        if ('HTTP_COOKIE' in env.keys() and len(env.get('HTTP_COOKIE')) != 0):
            print('HTTP_COOKIE', end='')
            # print(env['HTTP_COOKIE'])
            cookie.load(env['HTTP_COOKIE'])
            if 'session' in cookie.keys():
                self.session_id = cookie["session"].value
            else:
                self.session_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
                cookie['session'] = self.session_id

            print('HTTP_COOKIE: ', end='')
            # print(cookie)
            # print(len(cookie))
            
        else:
            self.session_id = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
            cookie['session'] = self.session_id

            print("HTTP_COOKIE not set!")

        self.sessions.setdefault(self.session_id, {})
        self.cookie = cookie
    

    def routing(self, env, start_response):  # routing
        request_method = env.get('REQUEST_METHOD')
        request_path = env.get('PATH_INFO')
        self.init_session(env)

        if (request_method == 'GET'):
            params = cgi.FieldStorage(environ=env, keep_blank_values=True)
            params = dict([(key, params[key].value) for key in params.keys()])
            print('GET', end=": ")
            print(params)

        elif (request_method == 'POST'):
            # print(env)
            wsgi_input = env['wsgi.input']
            content_length = int(env.get('CONTENT_LENGTH', 0))
            if (env['CONTENT_TYPE'] == 'application/json'):
                params = json.loads(wsgi_input.read(content_length))
            else:
                params = dict(parse_qsl(wsgi_input.read(content_length).decode('UTF-8')))
            print('POST', end=": ")
            print(params)

        allowed_request_method = {'GET', 'POST'}

        print(request_method)
        # GET, POST以外は404
        if request_method not in allowed_request_method:
            return self.bad_request(env, params)
        
        return self.router[request_method].get(request_path, self.not_found)(env, params=params)

    
    def get_statics(self, env, params={}):
        request_path = env.get('PATH_INFO')
        status = '200 OK'
        headers = [('Content-Type', 'text/{}; charset=utf-8'.format(params['type']))]
        try:
            with open('../'+request_path, 'r') as fp:
                contents = fp.read()
            contents = contents.encode('utf-8')
        except Exception as e:
            raise(e)
        
        body = [contents]
        return status, headers, body
 
 
    def redirect_to(self, env, to, params={}):
        home_url = util.application_uri(env)[:-1]
        redirect_url = home_url+to
        status = '303 See Other'
        headers = [('Content-type', 'text/html'), ('Location', redirect_url)]
        headers = set_cookie(headers, self.cookie)
        body = ["<p>リダイレクト中</p>".encode('utf-8')]

        return status, headers, body

    
    ####### @yumiya and @tanaka #######
    def game(self, env, params={}):
        if (self.session_id is None):
            return self.redirect_to(env, to='/', params=params)
        print('game')
        # print(self.cookie)
        # print(self.user_id)

        user = get_user(name=None, id=self.user_id)

        try:
            game_list = self.sessions[self.session_id].get('game', None)
            game = None if game_list is None else copy.deepcopy(game_list[-1])
            print(game)

            if (game is None):
                if (user['points'] < GAME_CONFIG['fee']):
                    with open('../template/game-result.html', 'r') as fp:
                        html = fp.read()
                        html = html.replace('{message}', '持ち点がゲーム参加に必要な{}ポイントに足りていません。'.format(GAME_CONFIG['fee']))
                    body = [html.encode('utf-8')]
                    status = '200 OK'
                    headers = [('Content-Type', 'text/html; charset=utf-8')]
                    headers = set_cookie(headers, self.cookie)

                    return status, headers, body

                print('game init')
                update_user_points(user['id'], user['points']-GAME_CONFIG['fee'])

                self.sessions[self.session_id]['game'] = []
                game = {'turn': 0, 'MAX': random.randint(15, 30), 'TURN_MAX': random.randint(3, 6), 'count': 0, 'turn_count': 0, 'my_count': 0, 'is_finished': 0 }
                
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                headers = set_cookie(headers, self.cookie)


            elif (game['is_finished'] != 0):
                print('finish')
                my_count = game['my_count']
                if (game['is_finished'] == 1):
                    point = my_count * GAME_CONFIG['mag']
                    message = 'YOU WIN！！\n{}ポイント獲得！！'.format(point)
                    update_user_points(self.user_id, user['points']+point)
                    user_status = '現在の所有ポイントは{}ポイントです。'.format(str(user['points']+point))

                elif (game['is_finished'] == -1):
                    message = 'YOU LOSE...'
                    user_status = '現在の所有ポイントは{}ポイントです。'.format(str(user['points']))
                
                with open('../template/game-result.html', 'r') as fp:
                    html = fp.read()
                    html = html.replace('{message}', message)
                    html = html.replace('{user_status}', user_status)
                body = [html.encode('utf-8')]

                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                headers = set_cookie(headers, self.cookie)

                self.sessions[self.session_id]['game'] = None
                return status, headers, body

            else:
                MAX = game['MAX']
                TURN_MAX = game['TURN_MAX']

                if ('plus' in params.keys()):
                    print('plus')
                    if (game['turn_count'] >= TURN_MAX):
                        return self.redirect_to(env, to='/home/game', params=params)

                    game['turn_count'] += 1
                    game['count'] += 1
                    game['my_count'] += 1

                    if (game['count'] >= MAX):
                        game['is_finished'] = -1

                        self.sessions[self.session_id]['game'] += [dict(game.items())]
                        gamelog = game_log(self.sessions[self.session_id].get('game', None))

                        return self.redirect_to(env, to='/home/game', params=params)

                    else:
                        pass

                elif ('submit' in params.keys()):
                    print('npc')
                    game["turn"] = 1
                    game['turn_count'] = 0

                    if (game['count'] == MAX-1):
                        game['count'] += 1
                        game['is_finished'] = 1
                        self.sessions[self.session_id]['game'] += [dict(game.items())]
                        gamelog = game_log(self.sessions[self.session_id].get('game', None))

                        return self.redirect_to(env, to='/home/game', params=params)

                    if (MAX-1 - game['count'] <= TURN_MAX):
                        while game["count"] < MAX -1:
                            game['count'] += 1
                            self.sessions[self.session_id]['game'] += [dict(game.items())]

                    else:
                        add = random.randint(1, TURN_MAX)
                        for _ in range(add-1):
                            game['count'] += 1
                            self.sessions[self.session_id]['game'] += [dict(game.items())]
                        game['count'] += 1
                        self.sessions[self.session_id]['game'] += [dict(game.items())]

                    game['turn'] = -1
                    self.sessions[self.session_id]['game'] += [dict(game.items())]

                    game["turn"] = 0
                
                else:
                    print('else')


            print('end: ', end='')

            self.sessions[self.session_id]['game'] += [dict(game.items())]
            gamelog = game_log(self.sessions[self.session_id].get('game', None))
        
            message = '{}に到達したら負け。<br>1ターンで{}回カウンターを増やせます。'.format(game['MAX'], game['TURN_MAX']-game['turn_count'])
            if (game['turn_count'] == 0):
                input_tag = \
                        """
                        <div class="form_contents">
                        <form method="POST" action='/home/game'>
                            <input class="send_btn" type="submit" id="plus" name="plus" value="+"/>
                        </form>
                        </div>
                        """
            elif (game['turn_count'] >= TURN_MAX):
                input_tag = \
                    """
                    <div class="form_contents">
                    <form method="POST" action='/home/game'>
                        <input class="send_btn" type="submit" id="submit" name="submit" value='ターン終了'/>
                    </form>
                    </div>
                    """
                game['turn_count'] = 0
                game['turn'] = -1
            else:
                input_tag = \
                        """
                        <div class="form_contents" style="width: 50%;">
                        <form method="POST" action='/home/game'>
                            <input class="send_btn" type="submit" id="submit" name="submit" value='ターン終了'/>
                        </form>
                        </div>
                        <div class="form_contents" style="width: 50%;">
                        <form method="POST" action='/home/game'>
                            <input class="send_btn" type="submit" id="plus" name="plus" value="+"/>
                        </form>
                        </div>
                        """
    
            # print(message)

            with open('../template/game.html', 'r', encoding='utf-8') as fp:
                html = fp.read()
                html = html.replace('{message}', message)
                # html = html.replace('{count}', str(game['count']))
                html = html.replace('{MAX}', str(game['MAX']))
                html = html.replace('{TURN_MAX}', str(game['TURN_MAX']))
                html = html.replace('{input_tag}', input_tag)
                html = html.replace('{log}', str(gamelog))
            body = [html.encode('utf-8')]

            status = '200 OK'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            headers = set_cookie(headers, self.cookie)

            return status, headers, body

        
        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        headers = set_cookie(headers, self.cookie)

        return status, headers, body


    def index(self, env, params={}):
        print('index')
        # print(self.cookie)
        try:
            error = self.sessions[self.session_id].get('error', None)
            if (error is None):
                error_tag = ''
            else:
                font_color = self.sessions[self.session_id].get('font_color', None)
                self.sessions[self.session_id] = {}

                error_tag = "<font color='{font_color}'>{error}</font>".format(font_color=font_color, error=error)
            with open('../template/index.html', 'r', encoding='utf-8') as fp:
                html = fp.read()
                html = html.replace('{error_tag}', error_tag)
            body = [html.encode('utf-8')]
        
        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        headers = set_cookie(headers, self.cookie)

        return status, headers, body


    def home(self, env, params={}):
        if (self.session_id is None):
            return self.redirect_to(env, to='/', params=params)
        print('home')
        # print(self.cookie)
        try:
            user = get_user(name=None, id=self.user_id)
            error = self.sessions[self.session_id].get('error', None)
            if (error is None):
                error_tag = ''
            else:
                font_color = self.sessions[self.session_id].get('font_color', None)
                self.sessions[self.session_id] = {}
                error_tag = "<font color='{font_color}'>{error}</font>".format(font_color=font_color, error=error)
            with open('../template/home.html', 'r', encoding='utf-8') as fp:
                html = fp.read()
                html = html.replace('{error_tag}', error_tag)
                html = html.replace('{name}', user['name'])
                html = html.replace('{id}', str(user['id']))
                html = html.replace('{points}', str(user['points']))
                html = html.replace('{fee}', str(GAME_CONFIG['fee']))
            body = [html.encode('utf-8')]
        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        headers = set_cookie(headers, self.cookie)

        return status, headers, body


    def logout(self, env, params={}):
        if (self.user_id is None):
            return self.redirect_to(env, to='/', params=params)
        self.user_id = None
        self.session_id = None
        self.sessions = {}

        return self.redirect_to(env, to='/', params={})

    # POST
    def login(self, env, params={}):
        try:
            name = params.get('name', 'guest')
            pwd = params.get('password', 'guest')
            params = {}

            res = get_user(name=name)

            print('login_user: ', end="")
            print(res)

            if (res is not None):
                if (check_pwd(res["password"], pwd)):
                    self.user_id = res['id']
                    print("認証成功")
                    # set_user_session(self.session_id, res['id'])
                    error_dict = {'error': 'login success', 'font_color': 'green'}
                    to = '/home'

                else:
                    print("認証失敗")
                    error_dict = {'error': 'authentification error', 'font_color': 'red'}
                    to = '/'

            else:
                print("ユーザーが存在しない。新規登録画面へ遷移")
                error_dict = {'error': 'user not found', 'font_color': 'red'}
                to = '/'


        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            # raise(e)
            return self.internal_server_error(env, params)

        
        self.sessions[self.session_id] = error_dict
        return self.redirect_to(env, to=to, params=params)

    # POST
    def signup(self, env, params={}):
        home_url = util.application_uri(env)
        try:
            name = params.get('name', 'guest')
            pwd = params.get('password', 'guest')
            params = {}
            # print("name: {}, pure_pwd: {}".format(name, pwd))

            res = get_user(name=name)
            print('signup_user: ', end="")
            print(res)

            if (res is not None):
                print("すでにユーザーが存在\nログイン画面へ遷移")
                error_dict = {'error': 'user already exiets', 'font_color': 'red'}
                redirect_url = home_url

            else:
                if (set_user(name, pwd)):
                    print("ユーザーの作成に成功")
                    error_dict = {'error': 'signup success', 'font_color': 'green'}
                    redirect_url = home_url

                else:
                    print("ユーザーの作成に失敗")
                    error_dict = {'error': 'signup failed', 'font_color': 'red'}
                    redirect_url = home_url

        except Exception as e:
            # print(str(e))
            # logging.error(str(e))
            raise(e)
            return self.internal_server_error(env, params)

        self.sessions[self.session_id] = error_dict
        status = '303 See Other'
        headers = [('Content-type', 'text/html'), ('Location', redirect_url)]
        headers = set_cookie(headers, self.cookie)
        body = ["<p>リダイレクト中</p>".encode('utf-8')]

        return status, headers, body


    def not_found(self, env, params={}):
        request_path = env['PATH_INFO']

        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Not Found: {}'.format(request_path)
        body = [body.encode('utf-8')]

        return status, headers, body


    def internal_server_error(self, env, params={}):
        request_method = env['REQUEST_METHOD']
        request_path = env['PATH_INFO']

        status = '500 INTERNAL SERVER ERROR'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Internal Server Error: {} {}'.format(request_method, request_path)
        body = [body.encode('utf-8')]

        return status, headers, body


    def bad_request(self, env, params={}):
        request_method = env['REQUEST_METHOD']
        request_path = env['PATH_INFO']

        status = '400 Bad Request'
        headers = [('Content-Type', 'text/plain; charset=utf-8')]
        body = 'Bad Request: {} {}'.format(request_method, request_path)
        body = [body.encode('utf-8')]

        return status, headers, body


db_init()
app = PageManager()
