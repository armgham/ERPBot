# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from multiprocessing import Process, Queue
from _thread import start_new_thread
import config


reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از سایت'],
                  ['گرفتن برنامه ترمهای قبل'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def get_bot():
    with open('bot_file', 'rb') as f:
        from pickle import load
        telegram_bot = load(f)
    return telegram_bot

class ProcessManager:
    queue = Queue()
    queue.put('empty')

    @staticmethod
    def run(target, args):
        start_new_thread(ProcessManager.run_join, (target, args))
    
    @staticmethod
    def run_join(target, args, run_as_thread=True):
        while ProcessManager.queue.get() == 'full':
            pass
        ProcessManager.main(target=target, args=args)

    @staticmethod
    def main(target, args):
        ProcessManager.queue.put('full')
        pr = Process(target=target, args=args)
        pr.daemon = True
        pr.start()
        pr.join()
        ProcessManager.queue.put('empty')
