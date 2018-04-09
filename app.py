# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import scrp
import _thread
import time_table_file
import re
import os



os.system('wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz')
os.system('tar -zxvf geckodriver-v0.11.1-linux64.tar.gz')
os.system('wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2')
os.system('tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2')
path = '/opt/app-root/src/phantomjs-2.1.1-linux-x86_64/bin'
os.environ["PATH"] += os.pathsep + path
os.environ["PATH"] += os.pathsep + '/opt/app-root/src'

CHOOSING, TYPING_REPLY, TYPING_CHOICE, USERPASS, START_TIME, FINISH_TIME, COMMENTS, LESSON, PROFESSOR, CHOOSING_DARS, DATE = range(11)

reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        'سلام! کار من اینه که با استفاده از یوزرنیم و پسورد erp وارد سامانه بشم'
        ' و برنامه تحصیلی تو رو به شکل منظمی دربیارم و تحویلت بدم!! شبیه عکس پروفایلم!',
        reply_markup=markup
    )
    return CHOOSING


def user_pass(bot, update, user_data):
    user_data['choice'] = 'username'
    update.message.reply_text('خب {} خودتو بده:'.format('نام کاربری'))
    return USERPASS


def received_userpass(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    if category == 'username':
        update.message.reply_text('خب {} خودتو بده:'.format('کلمه عبور'))
        user_data['choice'] = 'password'
        return USERPASS
    del user_data['choice']
    if 'time_table' in user_data:
        update.message.reply_text('خب الان برنامه رو از erp میگیرم!')
        _thread.start_new_thread(scrp.main, (user_data, bot, update))
        del user_data['time_table']
        bot.send_message(chat_id=update.message.chat.id, text='یه ذره صبر کن!')
        return CHOOSING
    update.message.reply_text('خب اطلاعات گرفته شد! الان میتونی برنامه رو از erp بگیری!',
                              reply_markup=markup)
    return CHOOSING


def time_table_scrp(bot, update, user_data):
    if 'username' not in user_data:
        user_data['time_table'] = 1
        update.message.reply_text('اول باید نام کاربری و کلمه عبور رو بفرستی!')
        bot.send_message(chat_id=update.message.chat_id, text='خب {} خودتو بده:'.format('نام کاربری'))
        user_data['choice'] = 'username'
        return USERPASS

    _thread.start_new_thread(scrp.main, (user_data, bot, update))
    bot.send_message(chat_id=update.message.chat.id, text='یه ذره صبر کن!')
    return CHOOSING


def time_table(bot, update, user_data):
    if 'exams' not in user_data:
        update.message.reply_text('اول برنامتو از erp بگیر بعد!', reply_markup=markup)
        return CHOOSING
    _thread.start_new_thread(time_table_file.main, (user_data, bot, update))
    return CHOOSING


def edit(bot, update, user_data):
    if 'exams' not in user_data:
        update.message.reply_text('تو که هنوز برنامه ای نداری که بخوای ویرایشش کنی!! اول برنامتو بگیر بعد!',
                                  reply_markup=markup)
        return CHOOSING
    edit_keyboard = [['میانترم'], ['ایجاد بخش جدید', 'حذف یک بخش']]
    edit_markup = ReplyKeyboardMarkup(edit_keyboard, one_time_keyboard=True)
    update.message.reply_text('یکی رو انتخاب کن (اگه وسط راه پشیمون شدی میتونی /cancel رو بفرستی):',
                              reply_markup=edit_markup)
    return CHOOSING


def midterm(bot, update, user_data):
    darss_keyboard = []
    for exam in user_data['exams']:
        darss_keyboard.append([exam[0:exam.find('   :   ')]])
    darss_markup = ReplyKeyboardMarkup(darss_keyboard, one_time_keyboard=True)
    update.message.reply_text('میانترم کدوم درس؟ :',
                              reply_markup=darss_markup)
    return CHOOSING_DARS


def received_dars(bot, update, user_data):
    dars = update.message.text
    for ind in range(len(user_data['midterm'])):
        if dars == user_data['midterm'][ind][0:user_data['midterm'][ind].find('  : ')]:
            user_data['midterm'].remove(user_data['midterm'][ind])
    user_data['edit'] = []
    user_data['edit'].append(dars)
    update.message.reply_text('خب توضیحات (مثلا تا کجا امتحانه یا هر چیز دیگه ای) با آخرش هم تاریخ میانترم رو به شکل yyyy/mm/dd بفرست :\n'
                              'مثلا: تا صفحه 72 فصل دو حذف : 1397/02/15')
    return DATE


def received_date(bot, update, user_data):
    date = update.message.text
    user_data['edit'].append(date)
    user_data['midterm'].append('  : '.join(user_data['edit']))
    del user_data['edit']
    _thread.start_new_thread(time_table_file.main, (user_data, bot, update))
    return CHOOSING


def day(bot, update, user_data):
    text = update.message.text
    if text == 'ایجاد بخش جدید':
        user_data['edit_mode'] = 'create'
    elif text == 'حذف یک بخش':
        user_data['edit_mode'] = 'remove'
    days_keyboard = [['شنبه', 'يکشنبه', 'دوشنبه'],
                     ['سه شنبه', 'چهارشنبه', 'پنجشنبه']]
    days_markup = ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True)
    update.message.reply_text('چه روزی؟ :', reply_markup=days_markup)
    return CHOOSING


def start_time(bot, update, user_data):
    text = update.message.text
    user_data['edit'] = []
    user_data['edit'].append(text)
    update.message.reply_text('ساعت شروع؟ (مثلا 8:00) :')
    return START_TIME


def received_start_time(bot, update, user_data):
    text = update.message.text
    if re.match(r'^\d{2}$', text):
        text += ':00'
    if re.match(r'^\d$', text):
        text = '0' + text + ':00'
    user_data['edit'].append(text)
    if user_data['edit_mode'] == 'remove':
        for str_part_time_table in user_data['info']:
            str_parts = str_part_time_table.split('\t')
            if str_parts[0] == user_data['edit'][0] and str_parts[1] == user_data['edit'][1]:
                user_data['info'].remove(str_part_time_table)
        del user_data['edit']
        _thread.start_new_thread(time_table_file.main, (user_data, bot, update))
        return CHOOSING
    update.message.reply_text('ساعت پایان؟ (مثلا 13:30) :')
    return FINISH_TIME


def received_finish_time(bot, update, user_data):
    text = update.message.text
    if re.match(r'^\d{1,2}$', text):
        text += ':00'
    user_data['edit'].append(text)
    update.message.reply_text('توضیحات؟ (مثلا کلاس کجا برگزار میشه مثل ک۳-فنی یا هر چیز دیگه ای) :')
    return COMMENTS


def received_comments(bot, update, user_data):
    text = update.message.text
    user_data['edit'].append(text)
    update.message.reply_text('درس؟ (مثلا حل تمرین ریاضی) :')
    return LESSON


def received_lesson(bot, update, user_data):
    text = update.message.text
    user_data['edit'].append(text)
    update.message.reply_text('اسم استاد یا ارائه دهنده :')
    return PROFESSOR


def received_professor(bot, update, user_data):
    text = update.message.text
    user_data['edit'].append(text)
    user_data['info'].append('\t'.join(user_data['edit']))
    del user_data['edit']
    _thread.start_new_thread(time_table_file.main, (user_data, bot, update))
    return CHOOSING


def cancel_edit(bot, update, user_data):
    update.message.reply_text('کنسل شد!', reply_markup=markup)
    del user_data['edit']
    return CHOOSING


def received_information(bot, update, user_data):
    text = update.message.text
    print(text)
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text('sss',
                              reply_markup=markup)
    return CHOOSING


def restart(bot, update, user_data):
    user_data.clear()
    update.message.reply_text('اطلاعاتت پاک شد.', reply_markup=markup)


def main():
    updater = Updater('517255695:AAFSQ549HEYNGhDCT3iC2dLgst1w5YPLOOA')

    dp = updater.dispatcher
    restart_command_handler = CommandHandler('restart', restart, pass_user_data=True)
    dp.add_handler(restart_command_handler)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^.*\(username\, password\)$',
                                    user_pass,
                                    pass_user_data=True),
                       RegexHandler('^گرفتن برنامه از erp$',
                                    time_table_scrp,
                                    pass_user_data=True),
                       RegexHandler('^ویرایش برنامه$',
                                    edit,
                                    pass_user_data=True),
                       RegexHandler('^(ایجاد بخش جدید|حذف یک بخش)$',
                                    day,
                                    pass_user_data=True),
                       RegexHandler('^گرفتن برنامه ویرایش شده$',
                                    time_table,
                                    pass_user_data=True),
                       RegexHandler('^(پنجشنبه|سه شنبه|دوشنبه|چهارشنبه|يکشنبه|شنبه)$',
                                    start_time,
                                    pass_user_data=True),
                       CommandHandler('cancel',
                                      cancel_edit,
                                      pass_user_data=True)],
           
            CHOOSING_DARS: [MessageHandler(Filters.text,
                                           received_dars,
                                           pass_user_data=True),
                            CommandHandler('cancel',
                                           cancel_edit,
                                           pass_user_data=True)
                            ],
            DATE: [RegexHandler('.*\d{4}\/\d{1,2}\/\d{1,2}.*',
                                received_date,
                                pass_user_data=True),
                   CommandHandler('cancel',
                                  cancel_edit,
                                  pass_user_data=True)
                   ],
            USERPASS: [MessageHandler(Filters.text,
                                      received_userpass,
                                      pass_user_data=True)],

            START_TIME: [RegexHandler('^\d{1,2}$',
                                      received_start_time,
                                      pass_user_data=True),
                         RegexHandler('^\d{1,2}\:\d{1,2}$',
                                      received_start_time,
                                      pass_user_data=True),
                         CommandHandler('cancel',
                                        cancel_edit,
                                        pass_user_data=True)],

            FINISH_TIME: [RegexHandler('^\d{1,2}$',
                                       received_finish_time,
                                       pass_user_data=True),
                          RegexHandler('^\d{1,2}\:\d{1,2}$',
                                       received_finish_time,
                                       pass_user_data=True),
                          CommandHandler('cancel',
                                         cancel_edit,
                                         pass_user_data=True)],

            COMMENTS: [MessageHandler(Filters.text,
                                      received_comments,
                                      pass_user_data=True),
                       CommandHandler('cancel',
                                      cancel_edit,
                                      pass_user_data=True)],

            LESSON: [MessageHandler(Filters.text,
                                    received_lesson,
                                    pass_user_data=True),
                     CommandHandler('cancel',
                                    cancel_edit,
                                    pass_user_data=True)],

            PROFESSOR: [MessageHandler(Filters.text,
                                       received_professor,
                                       pass_user_data=True),
                        CommandHandler('cancel',
                                       cancel_edit,
                                       pass_user_data=True)],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True)],
        },

        fallbacks=[]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

# '517255695:AAFSQ549HEYNGhDCT3iC2dLgst1w5YPLOOA'
