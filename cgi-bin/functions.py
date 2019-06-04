#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import bcrypt
import logging
from config import DB_NAME


def db_init():
    try:
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
        return True
    except Exception as e:
        logging.error(str(e))
        return False

def get_user(name):
    # データベース接続とカーソル生成
    con = sqlite3.connect(DB_NAME)
    con.text_factory = str
    con.row_factory = lambda cur, row: dict([(col[0], row[index]) for index, col in enumerate(cur.description)])
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

        #=-po7ktmg  return False

    con.commit()
    cur.close()
    con.close()

    return True

def hash_pwd(password, rounds=12):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds)).decode('utf8')


def check_pwd(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf8'), hashed_password.encode('utf8'))
