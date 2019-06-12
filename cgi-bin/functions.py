#! /usr/bin/env python3
# -*- coding: utf-8 -*-
####### @tanaka #######

import sqlite3
import bcrypt
import datetime
import logging
import sys
sys.path.append("/var/www/cgi-bin")
from config import DB_NAME, GAME_CONFIG


def db_init():
    try:
        # テーブルの作成
        con = sqlite3.connect(DB_NAME)
        con.text_factory = str
        cur = con.cursor()
        create_table = 'create table if not exists users (id integer primary key, name text, password text, points int)'
        try:
            cur.execute(create_table)
        except Exception as e:
            raise(e)

        # admin user
        create_table = 'insert into users (name, password, points) values ("admin", "$2b$12$1QE06Vbov8gz2Ssvp7PbbOg/Iwkoaiyy6njFsIiKoxiOQ3dKLOnJK", 100000000000)'
        try:
            cur.execute(create_table)
        except Exception as e:
            raise(e)
        create_table = 'create table if not exists sessions (id integer primary key, session_id text)'
        try:
            cur.execute(create_table)
        except Exception as e:
            raise(e)

        con.commit()
        cur.close()
        con.close()
        return True

    except Exception as e:
        # logging.error(str(e))
        raise(e)
        # return False

def get_user(name=None, id=None):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    con.text_factory = str
    con.row_factory = lambda cur, row: dict([(col[0], row[index]) for index, col in enumerate(cur.description)])
    cur = con.cursor()
    res = None
    if (id is not None):
        sql = 'select * from users where id = ?'
        res = cur.execute(sql, (id,)).fetchone()
    if (res is None) and (name is not None):
        sql = 'select * from users where name = ?'
        res = cur.execute(sql, (name,)).fetchone()
    # print(res)

    cur.close()
    con.close()

    return res

def set_user(name, pwd):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    sql = 'insert into users (name, password, points) values (?,?,?)'

    try:
        hashed_pwd = hash_pwd(pwd)
        print("hashed_pwd: {}".format(pwd))
        cur.execute(sql, (name, hashed_pwd, '5000'))
    except Exception as e:
        raise(e)

    con.commit()
    cur.close()
    con.close()

    return True

def set_user_session(session_id, user_id):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    sql = 'insert into sessions (session_id, id) values (?,?)'

    try:
        cur.execute(sql, (session_id, user_id))
    except Exception as e:
        raise(e)

    con.commit()
    cur.close()
    con.close()

    return True

def update_user_points(user_id, points):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    sql = 'update users set points = ? where id = ?'

    try:
        cur.execute(sql, (points, user_id))
    except Exception as e:
        raise(e)

    con.commit()
    cur.close()
    con.close()

    return True

####### @tanaka #######
def game_log(game):
    html = ''
    if (game is None):
        print('game is None')
        return html

    for i in range(len(game)):
        print(game[i])

    for i in range(len(game)):
        if (game[i]['turn'] == 0):
            if (i != 0) and ((game[i-1]["turn"] == 1) and (game[i]["turn"] == 0)):
                pass
            elif (i != 0) and (game[i-1]["count"] == game[i]["count"]):
                pass
            else:
                if (game[i]["count"] == 0):
                    pass
                else:
                    html += \
'''
<div class="chat_me">
    <div class="text">{count}</div>
    <span class="date">既読<br>{time}</span>
</div>

'''.format(count=game[i]["count"], time='{0:%H:%M}'.format(datetime.datetime.now()))
        elif (game[i]['turn'] == -1):
            html += \
'''
<div class="chat_opposite">
    <figure>
    <img src="https://1.bp.blogspot.com/-fyYoL91_tQo/Wp0Nn-VLocI/AAAAAAABKiI/3J2ywEvlbwIhjFNsmF8qpluPOg2it_HAQCLcBGAs/s800/ai_kanabou_buki.png" />
    </figure>
    <div class="chat_opposite-text">
    <div class="name">NPC</div>
    <div class="text">次はあなたの番です。</div>
    </div>
</div>
'''
        elif (game[i]['turn'] == 1):
            html += \
'''
<div class="chat_opposite">
    <figure>
    <img src="https://1.bp.blogspot.com/-fyYoL91_tQo/Wp0Nn-VLocI/AAAAAAABKiI/3J2ywEvlbwIhjFNsmF8qpluPOg2it_HAQCLcBGAs/s800/ai_kanabou_buki.png" />
    </figure>
    <div class="chat_opposite-text">
    <div class="name">NPC</div>
    <div class="text">{count}</div>
    </div>
</div>
'''.format(count=game[i]["count"])
    return html

####### @yumiya and @tanaka #######
# def game_log(game):
#     html = ''
#     if (game is None):
#         print('game is None')
#         return html

#     for i in range(len(game)):
#         print(game[i])

#     for i in range(len(game)):
#         if (game[i]['turn'] == 0):
#             if (i != 0) and ((game[i-1]["turn"] == 1) and (game[i]["turn"] == 0)):
#                 pass
#             elif (i != 0) and (game[i-1]["count"] == game[i]["count"]):
#                 pass
#             else:
#                 if (game[i]["count"] == 0):
#                     pass
#                 else:
#                     html += '<p>You {}</p>'.format(game[i]["count"])
#         elif (game[i]['turn'] == 1):
#             html += '<p>CPU {}</p>'.format(game[i]["count"])
#     return html


def hash_pwd(password, rounds=12):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds)).decode('utf8')


def check_pwd(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf8'), hashed_password.encode('utf8'))

def set_cookie(headers, cookie):
    print(cookie.output(header='', sep=''))
    headers += [('Set-Cookie', cookie.output(header='', sep=''))]

    print(headers)
    return headers
