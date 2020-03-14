# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
import MySQLdb
import config


reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def get_bot():
    with open('bot_file', 'rb') as f:
        from pickle import load
        telegram_bot = load(f)
    return telegram_bot
