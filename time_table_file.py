# -*- coding: utf-8 -*-
import os
import re
import telegram
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
import persian_reshaper
import matplotlib.font_manager as fm
from telegram import ReplyKeyboardMarkup

reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def ds(day):
    if day == get_display(persian_reshaper.reshape('شنبه')):
        return 0
    elif day == get_display(persian_reshaper.reshape('يکشنبه')):
        return 1
    elif day == get_display(persian_reshaper.reshape('دوشنبه')):
        return 2
    elif day == get_display(persian_reshaper.reshape('سه شنبه')):
        return 3
    elif day == get_display(persian_reshaper.reshape('چهارشنبه')):
        return 4
    elif day == get_display(persian_reshaper.reshape('پنجشنبه')):
        return 5
    return -1


def main(user_data, bot, update, from_scrp=False):
    days = []
    starts = []
    ends = []
    coms = []
    darss = []
    if from_scrp:
        data_of_time_table = user_data['scrp_info']
        del user_data['scrp_info']
    else:
        data_of_time_table = user_data['info']
    colors = ['pink', 'lightgreen', 'lightblue', 'crimson', 'salmon', 'yellow', 'silver', 'yellowgreen', 'y', 'tan',
              'orchid', 'c', 'aqua', 'deeppink']

    for line in data_of_time_table:
        data = line.split('\t')
        days.append(get_display(persian_reshaper.reshape(data[0])))
        starts.append(float(data[1].split(':')[0]) + float(data[1].split(':')[1]) / 60)
        ends.append(float(data[2].split(':')[0]) + float(data[2].split(':')[1]) / 60)
        if len(data) == 6:
            coms.append(get_display(persian_reshaper.reshape(data[3])))
        darss.append(get_display(persian_reshaper.reshape(data[4])))
    days2 = set(days)
    prop = fm.FontProperties(fname='XP ZibaBd.ttf')
    dd = dict((ds(x), x) for x in days2)
    sorted_days = []
    for key in sorted(dd):
        sorted_days.append(dd[key])

    darss = list(set(darss))
    nl = dict((darss[x], x) for x in range(len(darss)))
    mn = min(starts)
    mx = max(ends)
    fig = plt.figure(figsize=(16, 9))
    for i, line in zip(range(len(days)), data_of_time_table):
        data = line.split('\t')
        temp3 = []
        if len(data[3]) > 30:
            for iji in range(int(len(data[3]) / 32) + 1):
                temp3.append(data[3][iji * 32:32 * (iji + 1)])
            data[3] = '\n'.join(temp3)
        temp5 = []
        if len(data[5]) > 32:
            for ijl in range(int(len(data[5]) / 34) + 1):
                temp5.append(data[5][ijl * 34:34 * (ijl + 1)])
            data[5] = '\n'.join(temp5)

        plt.fill_between([starts[i] + 0.05, ends[i] - 0.05],
                         [sorted_days.index(days[i]) + 0.53, sorted_days.index(days[i]) + 0.53],
                         [sorted_days.index(days[i]) + 1.3, sorted_days.index(days[i]) + 1.43],
                         color=colors[nl[get_display(persian_reshaper.reshape(data[4]))]], edgecolor='red', linewidth=5)

        temp4 = []
        if len(data[4]) > 24:
            for ijk in range(int(len(data[4]) / 27) + 1):
                temp4.append(data[4][ijk * 27:27 * (ijk + 1)])
            data[4] = '\n'.join(temp4)

        plt.text(starts[i] + 0.25, sorted_days.index(days[i]) + 0.55,
                 '{0}:{1:0>2}'.format(int(data[1].split(':')[0]), int(data[1].split(':')[1])), va='top', fontsize=7)
        plt.text(ends[i] - 0.05, sorted_days.index(days[i]) + 0.55,
                 '{0}:{1:0>2}'.format(int(data[2].split(':')[0]), int(data[2].split(':')[1])), va='top', fontsize=7)
        plt.text((starts[i] + ends[i]) * 0.5,
                 (sorted_days.index(days[i]) + 0.5 + sorted_days.index(days[i]) + 1.4) * 0.5 - 0.2,
                 get_display(persian_reshaper.reshape(data[4])), ha='center', va='center', fontproperties=prop,
                 fontsize=13 - 1.5 * len(temp4))

        plt.text((starts[i] + ends[i]) * 0.5,
                 (sorted_days.index(days[i]) + sorted_days.index(days[i]) + 2.05) * 0.5,
                 get_display(persian_reshaper.reshape(data[3])), ha='center', va='center', fontsize=9 - len(temp3))
        plt.text((starts[i] + ends[i]) * 0.5,
                 (sorted_days.index(days[i]) + sorted_days.index(days[i]) + 2) * 0.5 + 0.23,
                 get_display(persian_reshaper.reshape(data[5])), ha='center', va='center', fontsize=8 - len(temp5))
    examsb = []
    for line in user_data['exams']:
        pattern = r'^.*(?P<y>\d{4})\/(?P<m>\d{2})\/(?P<d>\d{2}).*از ((?P<h>\d{2})\:\d{2}) تا.*$'
        examsb.append(re.search(pattern, line))

    exams = dict(
        (int(k.group('h')) / 24 + int(k.group('d')) + (int(k.group('m')) - 1) * 31 + (int(k.group('y')) - 1) * 31 * 12,
         list()) for k in examsb
        if k is not None)

    [exams[int(k.group('h')) / 24 + int(k.group('d')) + (int(k.group('m')) - 1) * 31 + (
            int(k.group('y')) - 1) * 31 * 12].append(k.group()) for k
     in examsb if k is not None]

    jj = 0
    exx = mx
    for key in sorted(exams):
        for j in exams[key]:
            if jj == 8:
                exx -= 4
                jj = 0
            plt.text(exx, (jj + 1.5 + 5.5 * len(sorted_days)) * 0.2, get_display(persian_reshaper.reshape(j)),
                     fontsize=11)
            jj += 1

    ax = fig.add_subplot(111)

    ax.set_ylim(len(days2) + 2 / 4, 0.4)
    ax.set_xlim(mx, mn)
    ax.set_yticks(range(1, len(days2) + 1))
    ax.set_yticklabels(sorted_days)
    ax.xaxis.grid()
    ax2 = ax.twiny().twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_xlim(ax.get_xlim())
    ax2.set_yticks(ax.get_yticks())
    ax2.set_yticklabels(sorted_days)
    plt.subplots_adjust(left=0.06, bottom=0.26, right=0.95, top=0.96, wspace=0.2, hspace=0.2)

    bot.send_message(chat_id=update.message.chat.id, text='داره میاد!!')
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
    plt.savefig('{0}.pdf'.format(user_data['username'] + 'barn'))
    plt.savefig('{0}.png'.format(user_data['username'] + 'barn'), dpi=120)
    bot.send_document(chat_id=update.message.chat.id, document=open('{0}.png'.format(user_data['username'] + 'barn'),
                                                                    'rb'))
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.UPLOAD_DOCUMENT)
    bot.send_document(chat_id=update.message.chat.id, document=open('{0}.pdf'.format(user_data['username'] + 'barn'),
                                                                    'rb'), reply_markup=markup)

    # plt.show()
    os.remove('{0}.png'.format(user_data['username'] + 'barn'))
    os.remove('{0}.pdf'.format(user_data['username'] + 'barn'))
    plt.close()
    # bot.send_message(chat_id=update.message.chat.id, text='میتونی حتی به برنامت اضافه هم بکنی:\n''/j')
