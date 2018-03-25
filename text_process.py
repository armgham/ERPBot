import re
from telegram import ReplyKeyboardMarkup


reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def main(user_data, bot, update):
    for line in user_data['first_info']:
        ostad = re.search(r'\t{2}\(\(\((?P<ostad>.*$)', line).group('ostad')
        dars = re.search(r'\t{3}(?P<dars>.*?)\t', line).group('dars')
        line = line[0:line.find('\t\t\t')]
        p = r'.*?(?=چهارشنبه|سه شنبه|دوشنبه|يکشنبه|شنبه)'
        p2 = r'(?P<day>چهارشنبه|سه شنبه|دوشنبه|يکشنبه|شنبه)\s+(?P<start>\d{2}\:\d{2})\s+\-\s+(?P<end>\d{2}\:\d{2})\s*'
        pb = r'(چهارشنبه|سه شنبه|دوشنبه|يکشنبه|شنبه)'
        while len(line) != 0:
            try:
                tozih = []

                xxx = [m.end(0) for m in re.finditer(p, line)][0]
                tozih.append(line[0:xxx])

                if len([m.start(0) for m in re.finditer(p2, line)]) == 0:
                    raise ValueError

                if [m.start(0) for m in re.finditer(pb, line)][0] != [m.start(0) for m in re.finditer(p2, line)][0]:
                    raise ValueError

                line = line[[m.end(0) for m in re.finditer(p, line)][0]:]
                total_time = line[0:[m.end(0) for m in re.finditer(p2, line)][0]]

                line = line[[(m.start(0), m.end(0)) for m in re.finditer(p2, line)][0][1]:]
                while not (re.sub('[()]', '', line.split(' ')[0]) in ostad or line.split(' ')[0] in '(هفته زوج)' or
                           line.split(' ')[0] in '(هفته فرد)') and len(line) != 0:
                    if len([m.start(0) for m in re.finditer(p2, line)]) != 0:
                        if [m.start(0) for m in re.finditer(p2, line)][0] != 0:
                            tozih.append(line.split(' ')[0])
                            line = line[line.find(' ') + 1:]
                        else:
                            break
                    elif len(line) != 0:
                        tozih.append(line)
                        line = ''
                zaman = re.search(p2, total_time)
                user_data['info'].append(
                    zaman.group('day') + '\t' + zaman.group('start') + '\t' + zaman.group('end') + '\t' + ' '.join(
                        tozih) + '\t' + dars + '\t' + ostad)
            except Exception as e:
                print(dars)
                print(e.args)
                dell = [line[0:[m.end(0) for m in re.finditer(pb, line)][0]]]
                line = line[[m.end(0) for m in re.finditer(pb, line)][0]:]
                while line[0] in ' \t':
                    line = line[1:]

                while not (re.sub('[()]', '', line.split(' ')[0]) in ostad or line.split(' ')[0] in '(هفته زوج)' or
                           line.split(' ')[0] in '(هفته فرد)') and len(line) != 0:
                    if len([m.start(0) for m in re.finditer(p2, line)]) != 0:
                        if [m.start(0) for m in re.finditer(p2, line)][0] != 0:
                            dell.append(line.split(' ')[0])
                            line = line[line.find(' ') + 1:]
                        else:
                            break
                    elif len(line) != 0:
                        dell.append(line)
                        line = ''

                bot.send_message(chat_id=update.message.chat.id, text='درس ' + dars + ' : \"' + ' '.join(
                    dell) + ' ' + ostad + ' \"' + 'یه مشکلی داره نتونستم بیارم تو برنامه. اگه خواستی مبتونی با '
                                                  'استفاده از (ویرایش برنامه) دستی یه بخش جدید به برنامه اضافه کنی',
                                 reply_markup=markup)
                continue

# main('950121230013')
