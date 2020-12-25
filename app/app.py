# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
# import scrp
import _thread
import re
import gc

import config
import time_table_file
import scrap_requets
import helpers
from multiprocessing import Process
from SqlPersistence import SqlPersistence
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


'''
import os 47
os.system('wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz')
os.system('tar -zxvf geckodriver-v0.11.1-linux64.tar.gz')
os.system('wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2')
os.system('tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2')
cwd = os.getcwd()
path = cwd + '/phantomjs-2.1.1-linux-x86_64/bin'
os.environ["PATH"] += os.pathsep + path
os.environ["PATH"] += os.pathsep + cwd
'''

#gc.set_threshold(1)
MAIN_CHOOSING, DAY_CHOOSING, EDIT_CHOOSING, USERPASS, \
    START_TIME, FINISH_TIME, COMMENTS, LESSON, PROFESSOR, CHOOSING_DARS, DATE = range(11)

markup = helpers.markup

def get_proxy():
    from SqlPersistence import get_database_connection
    db = get_database_connection(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DB_NAME)
    with db.cursor() as cur:
            results = cur.execute('SELECT * FROM PROXY')
            if results > 0:
                for proxy_address, in cur.fetchall():
                    if proxy_address == '':
                        return None
                    return {'http': 'socks4://'+proxy_address, 'https': 'socks4://'+proxy_address}
def get_protocol():
    from SqlPersistence import get_database_connection
    db = get_database_connection(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DB_NAME)
    with db.cursor() as cur:
            results = cur.execute('SELECT * FROM PROTOCOL')
            if results > 0:
                for protocol, in cur.fetchall():
                    return protocol

def start(update, context):
    update.message.reply_text(
        'سلام! کار من اینه که با استفاده از یوزرنیم و پسورد sada.guilan.ac.ir وارد سامانه بشم'
        ' و برنامه تحصیلی تو رو به شکل منظمی دربیارم و تحویلت بدم!! شبیه عکس پروفایلم!',
        reply_markup=markup
    )
    return MAIN_CHOOSING


def user_pass(update, context):
    user_data = context.user_data
    user_data['choice'] = 'username'
    update.message.reply_text('خب {} خودتو بده:'.format('نام کاربری'))
    return USERPASS


def received_userpass(update, context):
    user_data = context.user_data
    # bot = context.bot
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    if category == 'username':
        update.message.reply_text('خب {} خودتو بده:'.format('کلمه عبور'))
        user_data['choice'] = 'password'
        return USERPASS
    del user_data['choice']
    if 'time_table' in user_data:
        update.message.reply_text('خب الان برنامه رو از سایت میگیرم!')
        _thread.start_new_thread(scrap_requets.main, (user_data, update.message.chat_id, get_proxy(), get_protocol(), 'report', False, -1))
        del user_data['time_table']
        # bot.send_message(chat_id=update.message.chat.id, text='یه ذره صبر کن!')
        return MAIN_CHOOSING
    update.message.reply_text('خب اطلاعات گرفته شد! الان میتونی برنامه رو از سایت بگیری!',
                              reply_markup=markup)
    return MAIN_CHOOSING


def time_table_scrp(update, context):
    user_data = context.user_data
    bot = context.bot
    if 'username' not in user_data:
        user_data['time_table'] = 1
        update.message.reply_text('اول باید نام کاربری و کلمه عبور رو بفرستی!')
        bot.send_message(chat_id=update.message.chat_id, text='خب {} خودتو بده:'.format('نام کاربری'))
        user_data['choice'] = 'username'
        return USERPASS
    _thread.start_new_thread(scrap_requets.main, (user_data, update.message.chat_id, get_proxy(), get_protocol(), 'report', False, -1))
    # bot.send_message(chat_id=update.message.chat.id, text='یه ذره صبر کن!')
    return MAIN_CHOOSING


def time_table_scrp_debtor(update, context):
    user_data = context.user_data
    text = update.message.text
    prev = False
    term_n = -1
    if text == 'گرفتن برنامه ترمهای قبل':
        update.message.reply_text('الان لیست ترمها رو واست درمیارم' + '\nفقط ممکنه ترمای خیلی قبل مشکل داشته باشن چون طراحی سایت عوض شده تو این چند سال')
        prev = True
        term_n = -1
    elif text == '👈گرفتن برنامه از یه راه دیگه واسه دانشجوهایی که بدهی دارن':
        term_n = -1
        prev = False
    else:
        import re
        n = re.search(r'(?P<index_of_term>\d+) \: .*$', text).group('index_of_term')
        term_n = int(n)
        prev = True
    _thread.start_new_thread(scrap_requets.main, (user_data, update.message.chat_id, get_proxy(), get_protocol(), 'workbook', prev, term_n))
    return MAIN_CHOOSING


def eval_scrp(update, context):
    user_data = context.user_data
    if 'username' not in user_data:
        update.message.reply_text('اول باید نام کاربری و کلمه عبور رو بفرستی!', reply_markup=markup)
        return MAIN_CHOOSING
    update.message.reply_text('کاری که میکنم اینه که اسم استاد و درس رو بهت میگم و نمرش رو ازت میپرسم ۲۰ ثانیه وقت داری جواب بدی حالا این نمره رو به همه‌ی سوالا میدم فقط یکی از سوالا رو جواب متفاوت میدم که نظرت تو سیستم سایت ذخیره بشه چون اگه همه‌ی جوابا یه نمره باشه نظرت رو پاک میکنن!')

    user_data['nomre'] = -1
    #import eval_scrp_requests
    #_thread.start_new_thread(eval_scrp_requests.main, (user_data, update.message.chat_id, get_proxy(), get_protocol()))
    _thread.start_new_thread(scrap_requets.main, (user_data, update.message.chat_id, get_proxy(), get_protocol(), 'eval', False, -1))
    # bot.send_message(chat_id=update.message.chat.id, text='یه ذره صبر کن!')
    return MAIN_CHOOSING


def received_nomre(update, context):
    user_data = context.user_data
    nomre = update.message.text
    nomre = 20 - int(nomre)
    user_data['nomre'] = nomre

    return MAIN_CHOOSING


# def time_table_scrp_selenium(update, context):
#     user_data = context.user_data
#     _thread.start_new_thread(scrp.main, (user_data, update.message.chat_id))
#     update.message.reply_text('الان از یه روش دیگه میرم این یکی یه ذره طول میکشه!')
#     return MAIN_CHOOSING


def time_table(update, context):
    user_data = context.user_data
    if 'exams' not in user_data:
        update.message.reply_text('اول برنامتو از سایت بگیر بعد!', reply_markup=markup)
        return MAIN_CHOOSING
    helpers.ProcessManager.run(target=time_table_file.main, args=(user_data, update.message.chat_id))
    update.message.reply_text('ساختن تصویر برنامه ...')
    return MAIN_CHOOSING


def edit(update, context):
    user_data = context.user_data
    if 'exams' not in user_data:
        update.message.reply_text('تو که هنوز برنامه ای نداری که بخوای ویرایشش کنی!! اول برنامتو بگیر بعد!',
                                  reply_markup=markup)
        return MAIN_CHOOSING
    edit_keyboard = [['میانترم'], ['ایجاد بخش جدید', 'حذف یک بخش']]
    edit_markup = ReplyKeyboardMarkup(edit_keyboard, one_time_keyboard=True)
    update.message.reply_text('یکی رو انتخاب کن (اگه وسط راه پشیمون شدی میتونی /cancel رو بفرستی):',
                              reply_markup=edit_markup)
    return EDIT_CHOOSING


def midterm(update, context):
    user_data = context.user_data
    darss_keyboard = []
    for exam in user_data['exams']:
        darss_keyboard.append([exam[0:exam.find('   :   ')]])
    darss_markup = ReplyKeyboardMarkup(darss_keyboard, one_time_keyboard=True)
    update.message.reply_text('میانترم کدوم درس؟ :',
                              reply_markup=darss_markup)
    return CHOOSING_DARS


def received_dars(update, context):
    user_data = context.user_data
    dars = update.message.text
    for ind in range(len(user_data['midterm'])):
        if dars == user_data['midterm'][ind][0:user_data['midterm'][ind].find('  : ')]:
            user_data['midterm'].remove(user_data['midterm'][ind])
    user_data['edit'] = []
    user_data['edit'].append(dars)
    update.message.reply_text(
        'خب توضیحات (مثلا تا کجا امتحانه یا هر چیز دیگه ای) با آخرش هم تاریخ میانترم رو به شکل yyyy/mm/dd بفرست :\n'
        'مثلا: تا صفحه 72 فصل دو حذف : 1397/02/15')
    return DATE


def received_date(update, context):
    user_data = context.user_data
    date = update.message.text
    user_data['edit'].append(date)
    user_data['midterm'].append('  : '.join(user_data['edit']))
    del user_data['edit']
    helpers.ProcessManager.run(target=time_table_file.main, args=(user_data, update.message.chat_id))
    update.message.reply_text('ساختن تصویر برنامه ...')
    return MAIN_CHOOSING


def day(update, context):
    user_data = context.user_data
    text = update.message.text
    if text == 'ایجاد بخش جدید':
        user_data['edit_mode'] = 'create'
    elif text == 'حذف یک بخش':
        user_data['edit_mode'] = 'remove'
    days_keyboard = [['شنبه', 'يکشنبه', 'دوشنبه'],
                     ['سه شنبه', 'چهارشنبه', 'پنج شنبه']]
    days_markup = ReplyKeyboardMarkup(days_keyboard, one_time_keyboard=True)
    update.message.reply_text('چه روزی؟ :', reply_markup=days_markup)
    return DAY_CHOOSING


def start_time(update, context):
    user_data = context.user_data
    text = update.message.text
    user_data['edit'] = []
    user_data['edit'].append(text)
    update.message.reply_text('ساعت شروع؟ (مثلا 8:00) :')
    return START_TIME


def received_start_time(update, context):
    user_data = context.user_data
    text = update.message.text
    if re.match(r'^\d{2}$', text):
        text += ':00'
    if re.match(r'^\d$', text):
        text = '0' + text + ':00'
    if re.match(r'^\d\:\d{2}', text):
        text = '0' + text
    user_data['edit'].append(text)
    if user_data['edit_mode'] == 'remove':
        for str_part_time_table in user_data['info']:
            str_parts = str_part_time_table.split('\t')
            if str_parts[0] == user_data['edit'][0] and str_parts[1] == user_data['edit'][1]:
                user_data['info'].remove(str_part_time_table)
        del user_data['edit']

        helpers.ProcessManager.run(target=time_table_file.main, args=(user_data, update.message.chat_id))
        update.message.reply_text('ساختن تصویر برنامه ...')
        return MAIN_CHOOSING
    update.message.reply_text('ساعت پایان؟ (مثلا 13:30) :')
    return FINISH_TIME


def received_finish_time(update, context):
    user_data = context.user_data
    text = update.message.text
    if re.match(r'^\d{1,2}$', text):
        text += ':00'
    user_data['edit'].append(text)
    update.message.reply_text('توضیحات؟ (مثلا کلاس کجا برگزار میشه مثل ک۳-فنی یا هر چیز دیگه ای) :')
    return COMMENTS


def received_comments(update, context):
    user_data = context.user_data
    text = update.message.text
    user_data['edit'].append(text)
    update.message.reply_text('درس؟ (مثلا حل تمرین ریاضی) :')
    return LESSON


def received_lesson(update, context):
    user_data = context.user_data
    text = update.message.text
    user_data['edit'].append(text)
    update.message.reply_text('اسم استاد یا ارائه دهنده :')
    return PROFESSOR


def received_professor(update, context):
    user_data = context.user_data
    text = update.message.text
    user_data['edit'].append(text)
    user_data['info'].append('\t'.join(user_data['edit']))
    del user_data['edit']

    helpers.ProcessManager.run(target=time_table_file.main, args=(user_data, update.message.chat_id))
    update.message.reply_text('ساختن تصویر برنامه ...')
    return MAIN_CHOOSING


def cancel(update, context):
    user_data = context.user_data
    update.message.reply_text('کنسل شد!', reply_markup=markup)
    if 'edit' in user_data:
        del user_data['edit']
    if 'edit_mode' in user_data:
        del user_data['edit_mode']
    return MAIN_CHOOSING


def restart(update, context):
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text('اطلاعاتت پاک شد.', reply_markup=markup)
    return MAIN_CHOOSING


def unknown(update, context):
    update.message.reply_text('ورودی یا دستور نامعتبر!', reply_markup=markup)
    return MAIN_CHOOSING


def flush_database(update, context):
    context.dispatcher.persistence.update_flush()
    update.message.reply_text('ok', reply_markup=markup)
    return MAIN_CHOOSING


def add_proxy(update, context):
    logger.info(context.args)
    if len(context.args) == 1:
        proxy_address = context.args[0]
        logger.info(proxy_address)
    else:
        proxy_address = ''
    from SqlPersistence import get_database_connection
    db = get_database_connection(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DB_NAME)
    cur = db.cursor()
    cur.execute('DROP TABLE IF EXISTS PROXY;')
    cur.execute('CREATE TABLE PROXY (proxy VARCHAR(50));')
    db.commit()
    logger.info('in add proxy : ' + proxy_address)
    cur.execute('INSERT INTO PROXY VALUES (%s);', (proxy_address, ))
    db.commit()
    update.message.reply_text('ok', reply_markup=markup)
    db.close()
    return MAIN_CHOOSING

def switch_protocol(update, context):
    """ 's' for https and '' for http"""
    logger.info(context.args)
    if len(context.args) == 1:
        protocol = 's'
        logger.info(protocol)
    else:
        protocol = ''
    from SqlPersistence import get_database_connection
    db = get_database_connection(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DB_NAME)
    cur = db.cursor()
    cur.execute('DROP TABLE IF EXISTS PROTOCOL;')
    cur.execute('CREATE TABLE PROTOCOL (protocol VARCHAR(50));')
    db.commit()
    logger.info('in add PROTOCOL : ' + protocol)
    cur.execute('INSERT INTO PROTOCOL VALUES (%s);', (protocol, ))
    db.commit()
    update.message.reply_text('ok', reply_markup=markup)
    db.close()
    return MAIN_CHOOSING


def new_start(update, context):
    update.message.reply_text('سلام مجدد دوستان بات آپدیت شده. الان دیگه ویرایش هاتون احتمالا! ذخیره میشه و روند گرفتن برنامه از سایت هم سریعتر شده.', reply_markup=markup)
    return MAIN_CHOOSING


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # my_persistence = PicklePersistence('pfile', on_flush=True)
    
    sp = SqlPersistence(config.MYSQL_HOST, config.MYSQL_USERNAME, config.MYSQL_PASSWORD, config.MYSQL_DB_NAME,
                        store_user_data=True, store_chat_data=True, store_bot_data=False)
    updater = Updater(config.TOKEN, persistence=sp, use_context=True)

    telegram_bot = updater.bot
    with open('bot_file', 'wb') as bf:
        from pickle import dump
        dump(telegram_bot, bf)

    dp = updater.dispatcher
    restart_command_handler = CommandHandler('stop', restart, pass_user_data=True)
    dp.add_handler(restart_command_handler)
    

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(Filters.all, new_start)],

        states={
            MAIN_CHOOSING: [
                MessageHandler(Filters.regex(r'^.*\(username\, password\)$'), user_pass),
                MessageHandler(Filters.regex('^گرفتن برنامه از سایت$'), time_table_scrp),
                MessageHandler(Filters.regex('^ویرایش برنامه$'), edit),
                MessageHandler(Filters.regex('^گرفتن برنامه ویرایش شده$'), time_table),
                # MessageHandler(Filters.regex('^گرفتن برنامه از یه راه دیگه$'), time_table_scrp_selenium),
                MessageHandler(Filters.regex('^👈گرفتن برنامه از یه راه دیگه واسه دانشجوهایی که بدهی دارن$'), time_table_scrp_debtor),
                MessageHandler(Filters.regex('^گرفتن برنامه ترمهای قبل$'), time_table_scrp_debtor),
                MessageHandler(Filters.regex(r'^\d+ \: .*$'), time_table_scrp_debtor),
                MessageHandler(Filters.regex('12|13|14|20|12|15|16|17|18|19|20'), received_nomre),
                MessageHandler(Filters.regex('^💥پیچوندن فرم ارزیابی$'), eval_scrp),
            ],
    
            DAY_CHOOSING: [
                MessageHandler(Filters.regex('^(پنج شنبه|سه شنبه|دوشنبه|چهارشنبه|يکشنبه|شنبه)$'), start_time),
            ],

            EDIT_CHOOSING: [
                MessageHandler(Filters.regex('^میانترم$'), midterm),
                MessageHandler(Filters.regex('^(ایجاد بخش جدید|حذف یک بخش)$'), day),
            ],

            CHOOSING_DARS: [
                MessageHandler(Filters.text, received_dars),
            ],
                                  
            DATE: [
                MessageHandler(Filters.regex(r'.*\d{4}\/\d{1,2}\/\d{1,2}.*'), received_date),
            ],

            USERPASS: [
                MessageHandler(Filters.text, received_userpass),
            ],

            START_TIME: [
                MessageHandler(Filters.regex(r'^\d{1,2}$'), received_start_time),
                MessageHandler(Filters.regex(r'^\d{1,2}\:\d{1,2}$'), received_start_time),
            ],

            FINISH_TIME: [
                MessageHandler(Filters.regex(r'^\d{1,2}$'), received_finish_time),
                MessageHandler(Filters.regex(r'^\d{1,2}\:\d{1,2}$'), received_finish_time),
            ],

            COMMENTS: [
                MessageHandler(Filters.text, received_comments),
            ],

            LESSON: [
                MessageHandler(Filters.text, received_lesson),
            ],

            PROFESSOR: [
                MessageHandler(Filters.text, received_professor),
            ],
        },

        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('restart', restart),
            CommandHandler('cancel', cancel),
            CommandHandler('flush', flush_database),
            CommandHandler('addproxy', add_proxy),
            CommandHandler('sp', switch_protocol),
            MessageHandler(Filters.all, unknown),
        ],
        # allow_reentry=True,
        name="my_conversation",
        persistent=True
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logging.getLogger().info('hi.')
    main()
