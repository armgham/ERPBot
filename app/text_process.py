# -*- coding: utf-8 -*-
import helpers
import re
from telegram import ReplyKeyboardMarkup
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

markup = helpers.markup


def main(user_data, chat_id):
    user_data['scrp_info'] = []
    for lines in user_data['first_info']:
        ostad = re.search(r'\t{2}\(\(\((?P<ostad>.*$)', lines).group('ostad')
        dars = re.search(r'\t{3}(?P<dars>.*?)\t', lines).group('dars')
        lines = lines[0:lines.find('\t\t\t')]
        lines = list(filter(lambda x: x != '', lines.split('**')))
        p = r'(?P<first_comment>.*?)\s*(?P<day>چهارشنبه|سه شنبه|دوشنبه|يکشنبه|پنج شنبه|شنبه)\s*(?P<second_comment>.*?)\s*(?P<start>\d{2}\:\d{2})\s+\-\s+(?P<end>\d{2}\:\d{2})\s*(?P<last_comment>.*)'
        for line in lines:
            try:
                res = re.search(p, line)
                if res.group('day') == '' or res.group('start') == '' or res.group('end') == '':
                  raise ValueError
                user_data['scrp_info'].append(
                    res.group('day') + '\t' + res.group('start') + '\t' + res.group('end') + '\t' + ' '.join([res.group('first_comment'), res.group('second_comment'), res.group('last_comment')]) + '\t' + dars + '\t' + ostad)

            except Exception as e:
                logger.info(dars)
                logger.info(str(e.args))
                logger.info(str(user_data))
                
                bot = helpers.get_bot()
                bot.send_message(chat_id=chat_id, text='درس ' + dars + ' : \"' + line + ' ' + ostad + ' \"' + 'یه مشکلی داره نتونستم بیارم تو برنامه. اگه خواستی میتونی با '
                                                  'استفاده از (ویرایش برنامه) دستی یه بخش جدید به برنامه اضافه کنی',
                                 reply_markup=markup)
                continue
    logger.info('110')
    del user_data['first_info']
    if 'info' not in user_data:
        user_data['info'] = user_data['scrp_info']
# main('950122680007')
