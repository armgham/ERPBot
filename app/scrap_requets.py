import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
from bs4 import BeautifulSoup
import gc

from multiprocessing import Process
import text_process
import helpers
import time_table_file
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

markup = helpers.markup

class MyError(ValueError):
    def __init__(self, err_message=None, err_code=None):
        self.args = (err_message, err_code)


def main(user_data, chat_id, proxy):
    
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

        login_request = http.post('http://sada.guilan.ac.ir/SubSystem/Edari/PRelate/Site/SignIn.aspx', data=data, timeout=7, proxies=proxy)
        dashboard_param_search = re.search(r'\(\"http\:\/\/sada\.guilan\.ac\.ir\/Dashboard\.aspx\?param\=(?P<param>.*?)\"\)', login_request.text)

        if dashboard_param_search is None:
            if login_request.text.find('رمز عبور شما اشتباه ميباشد') >= 0 or login_request.text.find('نام کاربري يا کلمه عبور شما اشتباه ميباشد') >= 0:
                raise MyError('incorrect password_or_username', 'iup')  # incorrect username password
            else:
                raise Exception('dashbord_param or incorrect_password_or_username_message not found', 'dpnf')  # dashbord param not found

        dashboard_param = dashboard_param_search.group('param')

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='گرفتن فرم تثبیت انتخاب واحد ...')
        
        report_request = http.post('http://sada.guilan.ac.ir/Dashboard.aspx', params={'param': dashboard_param}, data={'Command': 'GET_TAB_INFO:020203'}, timeout=7, proxies=proxy)

        report_param_search = re.search(r'\/Subsystem\/Amozesh\/Sabtenam\/Tasbir\/Report\/Report\.aspx\?param\=(?P<param>.*)', report_request.text)
        if report_param_search is None:
            if report_request.text.find('بدهکار') >= 0:
                raise MyError('report problem because of debt', 'd')  # debt
            else:
                raise Exception('report_param or debt_message not found', 'rpnf')  # report param not found
        report_param = report_param_search.group('param')

        report_page = http.get('http://sada.guilan.ac.ir/Subsystem/Amozesh/Sabtenam/Tasbir/Report/Report.aspx', params={'param': report_param}, timeout=7, proxies=proxy)

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج اطلاعات از سایت ...')

        soup = BeautifulSoup(report_page.text, 'lxml')
        rows = soup.find_all('table', class_='grd')
        del soup, data, login_request, dashboard_param, dashboard_param_search, report_page, report_param_search, report_param, report_request

        for column_index in range(len(rows[0].find_all('td'))):
            if rows[0].find_all('td')[column_index].find('span').text == 'زمان برگزاري':
                time_column_index = column_index
        rows = rows[1:]
        number_of_rows = 0
        for row_index in range(len(rows)):
            try:
                int(rows[row_index].find_all('td')[0].find('span').text)
                number_of_rows = row_index

            except ValueError:
                break
        gc.collect()
        rows = rows[0:number_of_rows + 1]
        user_data['first_info'] = []
        user_data['midterm'] = []
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            user_data['first_info'].append(
                parts_of_row[time_column_index].find('span').text + '\t\t\t' + parts_of_row[2].find('span').text +
                '\t\t(((' + parts_of_row[time_column_index - 1].find(
                    'span').text.replace('\n ', '').replace('\n', ''))
        exams_time_column_index = -1
        for column_index in range(len(rows[0].find_all('td'))):
            if rows[0].find_all('td')[column_index].find('span').text == 'زمان امتحان':
                exams_time_column_index = column_index
        user_data['exams'] = []
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            user_data['exams'].append(parts_of_row[2].find('span').text + '   :   ' +
                                      parts_of_row[exams_time_column_index].find('span').text)

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='پردازش روی اطلاعات بدست اومده ...')
        text_process.main(user_data, chat_id)
        gc.collect()
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='ساختن تصویر برنامه ...')
        helpers.ProcessManager.run_join(target=time_table_file.main, args=(user_data, chat_id, True))

    except MyError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        error_code = e.args[-1]
        if error_code == 'iup':
            text_message = 'رمز عبور یا نام کاربری اشتباه'
        elif error_code == 'd':
            text_message = 'نیاوردن فرم تثبیت انتخاب واحد بدلیل بدهکار بودن دانشجو' + '\n'
            text_message += 'چون فرم تثبیت کار نکرده از یه راه دیگه میشه رفت الان یه دکمه دیگه اضافه کردم واست اونو میتونی امتحان کنی. منتها امتحانا رو نمیتونم واست لیست کنم.'

            reply_keyboard = [x.copy() for x in helpers.reply_keyboard]
            reply_keyboard[1].append('👈گرفتن برنامه از یه راه دیگه واسه دانشجوهایی که بدهی دارن')
            from telegram import ReplyKeyboardMarkup
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id, text='خب به ارور رسیدیم! : ' + text_message, reply_markup=markup)


    except Exception as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        
        bot.send_message(chat_id=chat_id, text='خب به ارور عجیبی برخوردیم!')
        
        reply_keyboard = [x.copy() for x in helpers.reply_keyboard]
        reply_keyboard[1].append('گرفتن برنامه از یه راه دیگه')
        from telegram import ReplyKeyboardMarkup
        new_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id, text='یه دکمه دیگه هم اضافه کردم :میتونی از یه راه دیگه هم تست کنی', reply_markup=new_markup)
        
        #import config
        #bot.send_message(chat_id=config.CHAT_ID_OF_ADMIN, text='ارور  ' + str(e.args), reply_markup=markup)

def debtor_main(user_data, chat_id, proxy):
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

        login_request = http.post('http://sada.guilan.ac.ir/SubSystem/Edari/PRelate/Site/SignIn.aspx', data=data, timeout=7, proxies=proxy)
        dashboard_param_search = re.search(r'\(\"http\:\/\/sada\.guilan\.ac\.ir\/Dashboard\.aspx\?param\=(?P<param>.*?)\"\)', login_request.text)

        if dashboard_param_search is None:
            if login_request.text.find('رمز عبور شما اشتباه ميباشد') >= 0 or login_request.text.find('نام کاربري يا کلمه عبور شما اشتباه ميباشد') >= 0:
                raise MyError('incorrect password_or_username', 'iup')  # incorrect username password
            else:
                raise Exception('dashbord_param or incorrect_password_or_username_message not found', 'dpnf')  # dashbord param not found

        dashboard_param = dashboard_param_search.group('param')

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='رفتن به قسمت کارنامه ترمی ...')
        
        workbook_request = http.post('http://sada.guilan.ac.ir/Dashboard.aspx', params={'param': dashboard_param}, data={'Command': 'GET_TAB_INFO:020205'}, timeout=7, proxies=proxy)

        workbook_param_search = re.search(r'\/Subsystem\/Amozesh\/Stu\/WorkBook\/StdWorkBook_Index\.aspx\?param\=(?P<param>.*)', workbook_request.text)
        if workbook_param_search is None:
            raise Exception('workbook_param not found', 'wpnf')  # workbook param not found
        workbook_param = workbook_param_search.group('param')

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='گرفتن فرم انتخاب واحد ترم آخر ...')
        request_for_last_term = http.get('http://sada.guilan.ac.ir/Subsystem/Amozesh/Stu/WorkBook/StdWorkBook_Index.aspx', params={'param': workbook_param}, timeout=7, proxies=proxy)
        last_term = BeautifulSoup(request_for_last_term.text, 'lxml')
        last_term = last_term.find(id='Term_Drp')
        last_term = last_term.find_all('option')[-1]['value']

        data={'SubIs_Chk':'false', 'Command':'Log:Vahed', 'Hitab':'Vahed', 'TypeCard_Drp':'rpGrade_Karname_2', 'mx_grid_info':'0;1;1;1;;;onGridLoad;1;;', 'Term_Drp':last_term}
        last_term_page = http.post('http://sada.guilan.ac.ir/Subsystem/Amozesh/Stu/WorkBook/StdWorkBook_Index.aspx', params={'param': workbook_param}, data=data, timeout=7, proxies=proxy)

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج اطلاعات از سایت ...')

        soup = BeautifulSoup(last_term_page.text, 'lxml')
        

        tables = soup.find_all('table')
        del soup, data, login_request, dashboard_param, dashboard_param_search, workbook_request, workbook_param_search, workbook_param, request_for_last_term, last_term_page

        user_data['first_info'] = []
        user_data['midterm'] = []
        user_data['exams'] = []
        time_column_index = 5
        for column_index, column in enumerate(tables[0].find_all('th')):
            if column.text == 'برنامه زماني':
                time_column_index = column_index
        table = tables[-1]
        rows = table.find_all('tr')
        for row_index, row in enumerate(rows):
            parts_of_row = row.find_all('td')
            user_data['first_info'].append(
                parts_of_row[time_column_index].text + '\t\t\t' + parts_of_row[1].text +
                '\t\t(((' + parts_of_row[time_column_index - 1].text.replace('\n ', ''))
        
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='پردازش روی اطلاعات بدست اومده ...')
        text_process.main(user_data, chat_id)
        gc.collect()
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='ساختن تصویر برنامه ...')
        helpers.ProcessManager.run_join(target=time_table_file.main, args=(user_data, chat_id, True))

    except MyError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        error_code = e.args[-1]
        if error_code == 'iup':
            text_message = 'رمز عبور یا نام کاربری اشتباه'
        bot.send_message(chat_id=chat_id, text='خب به ارور رسیدیم! : ' + text_message, reply_markup=markup)

    except Exception as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']) + '  debtor exception!!!!!!')
        logger.warning(str(e.args))
        bot.send_message(chat_id=chat_id, text='بازم ارور🤦‍♂️' + ' نمیدونم مشکل چیه. میتونی دوباره تست کنی اگه بازم درست نشد به این آیدی یه پیغام بفرست: @ArmanG98 🙏', reply_markup=markup)