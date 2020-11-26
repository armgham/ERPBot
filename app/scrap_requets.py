import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
import re
import json
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


class ScrapperUsingRequest:
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
        backoff_factor=1,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    
    def __init__(self, protocol, proxy):
        self.http.mount("https://", self.adapter)
        self.http.mount("http://", self.adapter)
        self.proxy = proxy
        self.main_url = f'http{protocol}://sada.guilan.ac.ir'

    
    def login(self, username, password):
        ## Old design of site
        # data = {
        #     'Command': 'LOGIN',
        #     'username': username,
        #     'password': password,
        #     #'SSMUsername_txt': user_data['username'],
        #     #'SSMPassword_txt': user_data['password'],
        # }
        # login_request = self.http.post('http'+self.protocol+'://sada.guilan.ac.ir/SubSystem/Edari/PRelate/Site/SignIn.aspx', data=data, timeout=7, proxies=self.proxy)
        # dashboard_param_search = re.search(r'\(\"http'+self.protocol+r'\:\/\/sada\.guilan\.ac\.ir\/Dashboard\.aspx\?param\=(?P<param>.*?)\"\)', login_request.text)
        # if dashboard_param_search is None:
        #     if login_request.text.find('رمز عبور شما اشتباه ميباشد') >= 0 or login_request.text.find('نام کاربري يا کلمه عبور شما اشتباه ميباشد') >= 0:
        #         raise MyError('incorrect password_or_username', 'iup')  # incorrect username password
        #     else:
        #         logger.info(login_request.text)
        #         raise Exception('dashbord_param or incorrect_password_or_username_message not found', 'dpnf')  # dashbord param not found
        # dashboard_param = dashboard_param_search.group('param')
        # return dashboard_param
        
        ## New design
        hs = self.http.headers
        hs['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0'
        hs['Accept'] = 'application/json, text/plain, */*'
        if 'Authentication' in hs:
            del hs['Authentication']
        if 'Authorization' in hs:
            del hs['Authorization']
        cipher = lambda p: '3'+'3'.join(list(p))
        self.http.get(f'{self.main_url}/Hermes', headers=hs, timeout=7, proxies=self.proxy)
        self.http.get(f'{self.main_url}/Hermes.html', timeout=7, proxies=self.proxy)

        d = {'inMethode_Name': '/api/Dashboard_Token_Initial', 'language': '', 'param': 'null', 'params': ''}
        ti_page = self.http.post(f'{self.main_url}/api/Dashboard_Token_Initial', data=d, timeout=7, proxies=self.proxy)

        hs = self.http.headers
        auth_token = json.loads(ti_page.text)['outInfoJson']
        hs['Authentication'] = 'Bearer ' + auth_token
        d2 = {'inMethode_Name': '/api/Dashboard_CheckIs', 'url': '/Hermes', 'param': 'null', 'params': ''}
        ci_page = self.http.post(f'{self.main_url}/api/Dashboard_CheckIs', data=d2, headers=hs, timeout=7, proxies=self.proxy)

        hs = self.http.headers
        access_token = json.loads(ci_page.text)['accessToken']
        hs['Authorization'] = 'Bearer ' + access_token
        d3 = {'inMethode_Name': '/api/Dashboard_Sign_CheckIs', 'hash': None}
        sci_page = self.http.post(f'{self.main_url}/api/Dashboard_Sign_CheckIs', data=json.dumps(d3), headers=hs, timeout=7, proxies=self.proxy)

        hs = self.http.headers
        access_token = json.loads(sci_page.text)['accessToken']
        hs['Authorization'] = 'Bearer ' + access_token
        d4 = {'inMethode_Name': '/api/Dashboard_Sign_In', 'hash': None, 'device': 'Desktop', 'Rememberme': False, 'cipher': cipher(password), 'userName': username}
        si_page = self.http.post(f'{self.main_url}/api/Dashboard_Sign_In', data=json.dumps(d4), headers=hs, timeout=7, proxies=self.proxy)
        si_j = json.loads(si_page.text)
        
        if si_j['outNumber'] == -1:
            raise MyError(err_message=si_j['outMessage'], err_code='fs') # from site
        hs = self.http.headers
        del hs['Authorization']
        auth_token = si_j['outInfoJson']
        hs['Authentication'] = 'Bearer ' + auth_token
        d = {'inMethode_Name': '/api/Dashboard_Token_Initial', 'language': '', 'param': 'null', 'params': ''}
        ti_page = self.http.post(f'{self.main_url}/api/Dashboard_Token_Initial', data=d, headers=hs, timeout=7, proxies=self.proxy)

        hs = self.http.headers
        auth_token = json.loads(ti_page.text)['outInfoJson']
        hs['Authentication'] = 'Bearer ' + auth_token
        d2 = {'inMethode_Name': '/api/Dashboard_CheckIs', 'url': '/Hermes', 'param': 'null', 'params': ''}
        ci_page = self.http.post(f'{self.main_url}/api/Dashboard_CheckIs', data=d2, headers=hs, timeout=7, proxies=self.proxy)

        access_token = json.loads(ci_page.text)['accessToken']
        return access_token

    def get_report(self, dashboard_param):
        # TODO: update for new design
        report_request = self.http.post(f'{self.main_url}/Dashboard.aspx', params={'param': dashboard_param}, data={'Command': 'GET_TAB_INFO:020203'}, timeout=7, proxies=self.proxy)

        report_param_search = re.search(r'\/Subsystem\/Amozesh\/Sabtenam\/Tasbir\/Report\/Report\.aspx\?param\=(?P<param>.*)', report_request.text)
        if report_param_search is None:
            if report_request.text.find('بدهکار') >= 0:
                raise MyError('report problem because of debt', 'd')  # debt
            elif 'eval' in report_request.text.lower():
                raise MyError('report problem because of evallist', 'eval')  # evalList
            else:
                logger.info(report_request.text)
                raise Exception('report_param or debt_message not found', 'rpnf')  # report param not found
        report_param = report_param_search.group('param')
        report_page = self.http.get(f'{self.main_url}/Subsystem/Amozesh/Sabtenam/Tasbir/Report/Report.aspx', params={'param': report_param}, timeout=7, proxies=self.proxy)
        return report_page

    def get_workbook(self, access_token): # dashboard_param):
        ## Old design
        # workbook_request = self.http.post('http'+self.protocol+'://sada.guilan.ac.ir/Dashboard.aspx', params={'param': dashboard_param}, data={'Command': 'GET_TAB_INFO:020205'}, timeout=7, proxies=self.proxy)
        # workbook_param_search = re.search(r'\/Subsystem\/Amozesh\/Stu\/WorkBook\/StdWorkBook_Index\.aspx\?param\=(?P<param>.*)', workbook_request.text)
        # if workbook_param_search is None:
        #     raise Exception('workbook_param not found', 'wpnf')  # workbook param not found
        # workbook_param = workbook_param_search.group('param')
        # return workbook_param

        hs = self.http.headers
        hs['Authorization'] = 'Bearer ' + access_token
        profile_page = self.http.post(f'{self.main_url}/api/Dashbord_Profile_Std_CheckIs', data={'inMethode_Name': '/api/Dashbord_Profile_Std_CheckIs'}, headers=hs, timeout=7, proxies=self.proxy)
        menu_access_token = json.loads(profile_page.text)['accessToken']
        menu_hs = self.http.headers
        menu_hs['Authorization'] = 'Bearer ' + menu_access_token
        menu_page = self.http.post(f'{self.main_url}/api/Core_Menu_User', data={'inMethode_Name': '/api/Core_Menu_User'}, headers=menu_hs ,timeout=7, proxies=self.proxy)
        id_menu_2 = ''
        j = json.loads(menu_page.text)
        for rc in j:
            if rc['hafmanCode'] == '0202':
                for c in rc['childs']:
                    if c['hafmanCode'] == '020205':
                        id_menu_2 = c['idMenu2']
        hs = self.http.headers
        hs['Authorization'] = 'Bearer ' + access_token
        d = {'idMenu2': id_menu_2, 'inMethode_Name': '/api/Core_Menu_Run'}
        tran_page = self.http.post(f'{self.main_url}/SubSystem/Angular_Tran.aspx', data=json.dumps(d), headers=hs, timeout=7, proxies=self.proxy)
        workbook_param = json.loads(tran_page.text)['outInfoJson']
        return workbook_param.replace('/Subsystem/Amozesh/Stu/WorkBook/StdWorkBook_Index.aspx?param=', '')
        

    def get_term(self, workbook_param, prev_term, number_of_term):
        request_for_term = self.http.get(f'{self.main_url}/Subsystem/Amozesh/Stu/WorkBook/StdWorkBook_Index.aspx', params={'param': workbook_param}, timeout=15, proxies=self.proxy)
        all_terms = BeautifulSoup(request_for_term.text, 'lxml')
        all_terms = all_terms.find(id='Term_Drp')
        if not prev_term:
            term = all_terms.find_all('option')[-1]['value']
        else:
            if number_of_term != -1:
                term = all_terms.find_all('option')[number_of_term]['value']
            else:
                terms_keyboard = []
                for term_index, term_str in enumerate(all_terms.find_all('option')[1:]):
                    terms_keyboard.append([str(term_index+1) + ' : ' + term_str.text])
                return terms_keyboard
        data={'SubIs_Chk':'false', 'Command':'Log:Vahed', 'Hitab':'Vahed', 'TypeCard_Drp':'rpGrade_Karname_2', 'mx_grid_info':'0;1;1;1;;;onGridLoad;1;;', 'Term_Drp':term}
        term_page = self.http.post(f'{self.main_url}/Subsystem/Amozesh/Stu/WorkBook/StdWorkBook_Index.aspx', params={'param': workbook_param}, data=data, timeout=10, proxies=self.proxy)
        return term_page
    
    def get_infos_from_term_page(self, term_page_text):
        info = []
        soup = BeautifulSoup(term_page_text, 'lxml')
        tables = soup.find_all('table')
        
        time_column_index = 5
        for column_index, column in enumerate(tables[0].find_all('th')):
            if column.text == 'برنامه زماني':
                time_column_index = column_index
        table = tables[-1]
        rows = table.find_all('tr')
        for _, row in enumerate(rows):
            parts_of_row = row.find_all('td')
            info.append(
                parts_of_row[time_column_index].text + '\t\t\t' + parts_of_row[1].text +
                '\t\t(((' + parts_of_row[time_column_index - 1].text.replace('\n ', ''))
        return {'tabel': info, 'midterm': [], 'exams': []}

    def get_infos_from_report_page(self, report_page_text):
        info = []
        soup = BeautifulSoup(report_page_text, 'lxml')
        rows = soup.find_all('table', class_='grd')
        time_column_index = -1
        for column_index in range(len(rows[0].find_all('td'))):
            if rows[0].find_all('td')[column_index].find('span').text == 'زمان برگزاري':
                time_column_index = column_index
        if time_column_index == -1:
            raise MyError('table is empty', 'empty')
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
        
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            info.append(
                parts_of_row[time_column_index].find('span').text + '\t\t\t' + parts_of_row[2].find('span').text +
                '\t\t(((' + parts_of_row[time_column_index - 1].find(
                    'span').text.replace('\n ', '').replace('\n', ''))
        exams_time_column_index = -1
        for column_index in range(len(rows[0].find_all('td'))):
            if rows[0].find_all('td')[column_index].find('span').text == 'زمان امتحان':
                exams_time_column_index = column_index
        exams_info = []
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            exams_info.append(parts_of_row[2].find('span').text + '   :   ' +
                                      parts_of_row[exams_time_column_index].find('span').text)

        return {'tabel': info, 'midterm': [], 'exams': exams_info}


# way : report or workbook
def main(user_data, chat_id, proxy, protocol='s', way='report', prev_term=False, number_of_term=-1):
    try:
        bot = helpers.get_bot()
        scrapper = ScrapperUsingRequest(protocol=protocol, proxy=proxy)
        
        sent_message = bot.send_message(chat_id=chat_id, text='وارد شدن با یوزرنیم و پسورد ...')
        sent_message = sent_message.message_id

        # dash_param = scrapper.login(user_data['username'], user_data['password'])
        dashboard_access_token = scrapper.login(user_data['username'], user_data['password'])
        
        if way == 'report':
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='گرفتن فرم تثبیت انتخاب واحد ...')
            bot.send_message(chat_id=chat_id, text='فرم تثبیت تو سایت نیستش. از دکمه (گرفتن برنامه ترمهای قبل) استفاده کن و ترم آخر رو انتخاب کن', reply_markup=markup)
            return 11
            # TODO: update for new design
            report_page = scrapper.get_report(dashboard_access_token)
            
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج اطلاعات از سایت ...')
            
            infos = scrapper.get_infos_from_report_page(report_page.text)
        elif way == 'workbook':
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='رفتن به قسمت کارنامه ترمی ...')

            workbook_param = scrapper.get_workbook(dashboard_access_token)
            
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='گرفتن فرم انتخاب واحد ترم ' + ('موردنظر' if prev_term else 'آخر') + ' ...')
            if prev_term and number_of_term == -1:
                from telegram import ReplyKeyboardMarkup
                terms_keyboard = scrapper.get_term(workbook_param, prev_term, number_of_term)
                terms_markup = ReplyKeyboardMarkup(terms_keyboard, one_time_keyboard=True)
                bot.send_message(chat_id=chat_id, text='برنامه کدوم ترم:؟',
                                        reply_markup=terms_markup)
                return 11
            term_page = scrapper.get_term(workbook_param, prev_term, number_of_term)
            
            bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج اطلاعات از سایت ...')
            infos = scrapper.get_infos_from_term_page(term_page.text)
            
        user_data['first_info'] = infos['tabel']
        user_data['midterm'] = infos['midterm']
        user_data['exams'] = infos['exams']
        
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='پردازش روی اطلاعات بدست اومده ...')
        text_process.main(user_data, chat_id)
        gc.collect()
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='ساختن تصویر برنامه ...')
        helpers.ProcessManager.run_join(target=time_table_file.main, args=(user_data, chat_id, True))

    except MyError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        error_code = e.args[-1]
        if error_code == 'fs':
            text_message = e.args[0]
        # elif error_code == 'iup':
        #     text_message = 'رمز عبور یا نام کاربری اشتباه'
        #     markup = helpers.markup
        # elif error_code == 'empty':
        #     text_message = 'جدول این ترم خالیه شاید تو ترم تابستون باشی و واحد نداشته باشی' + '\nمیتونی واسه ترمهای قبل رو بگیری'
        #     markup = helpers.markup
        # elif error_code == 'd':
        #     text_message = 'نیاوردن فرم تثبیت انتخاب واحد بدلیل بدهکار بودن دانشجو' + '\n'
        #     text_message += 'چون فرم تثبیت کار نکرده از یه راه دیگه میشه رفت الان یه دکمه دیگه اضافه کردم واست اونو میتونی امتحان کنی. منتها امتحانا رو نمیتونم واست لیست کنم.'

        #     reply_keyboard = [x.copy() for x in helpers.reply_keyboard]
        #     reply_keyboard[1].append('👈گرفتن برنامه از یه راه دیگه واسه دانشجوهایی که بدهی دارن')
        #     from telegram import ReplyKeyboardMarkup
        #     markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        # elif error_code == 'eval':
        #     text_message = 'مثل اینکه باید فرم ارزیابی اساتید رو پر کنی.' + '\n'
        #     text_message += 'اگه حال نداری همه‌ی سوالای ارزشیابی رو جواب بدی میتونی از دکمه پیچوندن فرم ارزیابی استفاده کنی!'
        #     markup = helpers.markup
        bot.send_message(chat_id=chat_id, text='خب به ارور رسیدیم! : ' + text_message, reply_markup=markup)

    except ConnectionError as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        logger.warning('CONECTION PROBLEM (WITH PROXY or maybe WITHOUT PROXY)')
        bot.send_message(chat_id=chat_id, text='مشکل در ارتباط با سایت!!! شاید سایت خراب باشه یا شاید بازم سایت رو یه کاری کردن فقط با آیپی ایران بشه رفت و سرور این ربات هم خارج از ایرانه.' +
                                                ' اگه پراکسی ساکس۴ ایران داری ممنون میشم واسه این آیدی بفرستیش' + ': @ArmanG98\n' + 'میتونی دوباره تست کنی. اگه سایت اوکی بود و بازم همین' +
                                                ' ارور رو دیدی چند ساعت دیگه دوباره امتحان کن. ', reply_markup=helpers.markup)
        from config import CHAT_ID_OF_ADMIN
        bot.send_message(chat_id=CHAT_ID_OF_ADMIN, text='hi admin! fix connection problem please!', reply_markup=helpers.markup)

    except Exception as e:
        logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        logger.warning(str(e.args))
        
        bot.send_message(chat_id=chat_id, text='خب به ارور عجیبی برخوردیم!', reply_markup=helpers.markup)
        
        # reply_keyboard = [x.copy() for x in helpers.reply_keyboard]
        # reply_keyboard[1].append('گرفتن برنامه از یه راه دیگه')
        # from telegram import ReplyKeyboardMarkup
        # new_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        # bot.send_message(chat_id=chat_id, text='یه دکمه دیگه هم اضافه کردم :میتونی از یه راه دیگه هم تست کنی', reply_markup=new_markup)
        
        # #import config
        # #bot.send_message(chat_id=config.CHAT_ID_OF_ADMIN, text='ارور  ' + str(e.args), reply_markup=markup)