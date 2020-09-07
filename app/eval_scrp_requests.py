import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import gc
from requests.exceptions import ConnectionError

import helpers

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


class MyError(ValueError):
    def __init__(self, err_message=None, err_code=None):
        self.args = (err_message, err_code)


def main(user_data, chat_id, proxy, protocol='s'):
    markup = helpers.markup
    score_markup = helpers.score_markup
    
    try:
        bot = helpers.get_bot()

        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        data = {
            'Command': 'LOGIN',
            'username': user_data['username'],
            'password': user_data['password'],
            #'SSMUsername_txt': user_data['username'],
            #'SSMPassword_txt': user_data['password'],
        }
        sent_message = bot.send_message(chat_id=chat_id, text='وارد شدن با یوزرنیم و پسورد ...')
        sent_message = sent_message.message_id

        login_request = http.post('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Edari/PRelate/Site/SignIn.aspx', data=data, timeout=7, proxies=proxy)
        dashboard_param_search = re.search(r'\(\"http'+protocol+r'\:\/\/sada\.guilan\.ac\.ir\/Dashboard\.aspx\?param\=(?P<param>.*?)\"\)', login_request.text)

        if dashboard_param_search is None:
            if login_request.text.find('رمز عبور شما اشتباه ميباشد') >= 0 or login_request.text.find('نام کاربري يا کلمه عبور شما اشتباه ميباشد') >= 0:
                raise MyError('incorrect password_or_username', 'iup')  # incorrect username password
            else:
                raise Exception('dashbord_param or incorrect_password_or_username_message not found', 'dpnf')  # dashbord param not found

        dashboard_param = dashboard_param_search.group('param')

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='رفتن به قسمت فرم تثبیت انتخاب واحد ...')
        
        report_request = http.post('https://sada.guilan.ac.ir/Dashboard.aspx', params={'param': dashboard_param}, data={'Command': 'GET_TAB_INFO:020203'}, timeout=7, proxies=proxy)

        report_param_search = re.search(r'\/Subsystem\/Amozesh\/Sabtenam\/Tasbir\/Report\/Report\.aspx\?param\=(?P<param>.*)', report_request.text)
        if report_param_search is not None:
            raise MyError('evalList not found', 'not_eval')  # evalList
            
        else:
            if report_request.text.find('بدهکار') >= 0:
                raise MyError('report problem because of debt', 'd')  # debt
            elif 'eval' in report_request.text.lower():
                
                evalList_param_search =  re.search(r'\/SubSystem\/Amozesh\/Eval\/List\/EvalList\.aspx\?param\=(?P<param>.*)', report_request.text)
                evalList_param = evalList_param_search.group('param')

                evalList_page = http.get('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/List/EvalList.aspx', params={'param': evalList_param}, timeout=7, proxies=proxy)

                bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج لیست ارزشیابی‌ها ...')
                
                soup = BeautifulSoup(evalList_page.text, 'lxml')
                eval_list = soup.find_all('table')[-1].find_all('tr')
                while eval_list:
                    eval_elem = eval_list.pop()
                    
                    Command_data = 'AnswerSubject♥' + eval_elem.find_all('td')[0].text + '♥' + eval_elem.find_all('td')[3].text
                    
                    eval_request = http.post('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/List/EvalList.aspx', params={'param': evalList_param}, data={'Command': Command_data}, timeout=7, proxies=proxy)
                    eval_param = eval_request.text
                    eval_page = http.get('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/Answer/Subject/EvalAnswerSubject.aspx', params={'param': eval_param}, timeout=7, proxies=proxy)
                    
                    bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج لیست استادها ...')

                    inner_soup = BeautifulSoup(eval_page.text, 'lxml')
                    professor_list = inner_soup.find_all('table')[-1].find_all('tr')

                    while professor_list:
                        professor_elem = professor_list[-1]
                        Command_data = 'Answer♥' + professor_elem.find_all('td')[0].text + '♥' + professor_elem.find_all('td')[1].text + '♥' + professor_elem.find_all('td')[2].text +\
                                        '♥' + professor_elem.find_all('td')[3].text + '♥' + professor_elem.find_all('td')[4].text + '♥' + professor_elem.find_all('td')[7].text
                        
                        professor_request = http.post('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/Answer/Subject/EvalAnswerSubject.aspx', params={'param': eval_param}, data={'Command': Command_data}, timeout=7, proxies=proxy)
                        questions_param = professor_request.text
                        questions_page = http.get('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/Answer/ListItems.aspx', params={'param': questions_param}, timeout=7, proxies=proxy)
                        bot.send_message(chat_id=chat_id, text=professor_elem.find_all('td')[7].text + '    ' + professor_elem.find_all('td')[8].text + '\n نمره رو بزن:' , reply_markup=score_markup)
                        timer = 0
                        while timer <= 20:
                            if user_data['nomre'] == -1:
                                if timer == 20:
                                    bot.send_message(chat_id=chat_id, text='خب تایمت تموم شد! بای بای!', reply_markup=markup)
                                    return -1
                                sleep(1.1)
                                timer += 1
                            else:
                                break
                        score = user_data['nomre']
                        qs_soup = BeautifulSoup(questions_page.text, 'lxml')
                        qs = qs_soup.find_all('table')[-1].find_all('tr')
                        x = 'Insert:??*'
                        post_data = {}
                        one_random_q = randint(0, len(qs)-1)
                        for q_i, q in enumerate(qs):
                            nomre = score
                            if len(q.find_all('td')) > 3:
                                x += q.find_all('td')[3].text
                            x += '?'
                            if q_i == one_random_q:
                                if nomre == 8:
                                    nomre -= 1
                                elif nomre == 0:
                                    nomre += 1
                                else:
                                    nomre = nomre + [1, -1][randint(0, 1)]
                            for inp_el in q.find_all('input'):
                                # nomre = 1 # means 19
                                if inp_el['id'][:3] == 'rb' + str(nomre):
                                    post_data[inp_el['id']] = 'true'
                                    x += inp_el['value']
                            x += '?'
                            x += q.find_all('td')[10].text
                            x += '*'
                        x += ':'
                        post_data['Command'] = x
                        logger.info('EVALLLLLLLL  '+str(post_data))
                        professor_eval_request = http.post('http'+protocol+'://sada.guilan.ac.ir/SubSystem/Amozesh/Eval/Answer/ListItems.aspx', params={'param': questions_param}, data=post_data, timeout=7, proxies=proxy)
                        if 'ok' in professor_eval_request.text.lower():
                            professor_list.pop()
                        else:
                            bot.send_message(chat_id=chat_id, text='عه فکر کنم نمره ثبت نشد. دوباره !!')
                        user_data['nomre'] = -1
                bot.send_message(chat_id=chat_id, text='خب تموم شششددددد !!!!!', reply_markup=markup)
                del soup, qs_soup, inner_soup


    except MyError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        error_code = e.args[-1]
        if error_code == 'iup':
            text_message = 'رمز عبور یا نام کاربری اشتباه'
            markup = helpers.markup
        elif error_code == 'd':
            text_message = 'نیاوردن فرم تثبیت انتخاب واحد بدلیل بدهکار بودن دانشجو'
            markup = helpers.markup
        elif error_code == 'not_eval':
            text_message = 'مثل اینکه فرم ارزیابی پیدا نشده.'
            markup = helpers.markup
        bot.send_message(chat_id=chat_id, text='خب به ارور رسیدیم! : ' + text_message, reply_markup=markup)

    except ConnectionError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        logger.warning('CONECTION PROBLEM (WITH PROXY or maybe WITHOUT PROXY)')
        bot.send_message(chat_id=chat_id, text='مشکل در ارتباط با سایت!!! شاید سایت خراب باشه یا شاید بازم سایت رو یه کاری کردن فقط با آیپی ایران بشه رفت و سرور این ربات هم خارج از ایرانه.' +
                                                ' اگه پراکسی ساکس۴ ایران داری ممنون میشم واسه این آیدی بفرستیش' + ': @ArmanG98\n' + 'میتونی دوباره تست کنی. اگه سایت اوکی بود و بازم همین' +
                                                ' ارور رو دیدی چند ساعت دیگه دوباره امتحان کن. ', reply_markup=helpers.markup)
        from config import CHAT_ID_OF_ADMIN
        bot.send_message(chat_id=CHAT_ID_OF_ADMIN, text='', reply_markup=helpers.markup)

    except Exception as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        markup = helpers.markup
        bot.send_message(chat_id=chat_id, text='خب به ارور عجیبی برخوردیم!', reply_markup=markup)
        
        #import config
        #bot.send_message(chat_id=config.CHAT_ID_OF_ADMIN, text='ارور  ' + str(e.args), reply_markup=markup)
