# -*- coding: utf-8 -*-
from multiprocessing import Process
from urllib3.exceptions import ProtocolError
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium import webdriver
# from selenium.webdriver.firefox.options import Options

# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
from bs4 import BeautifulSoup
import text_process
import helpers
import time_table_file

import gc
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

markup = helpers.markup

def main(user_data, chat_id):
    '''
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:8910',
        desired_capabilities=DesiredCapabilities.PHANTOMJS)
    '''
    bot = helpers.get_bot()
    sleep(0.1)
    sent_message = bot.send_message(chat_id=chat_id, text='باز کردن مرورگر')
    sent_message = sent_message.message_id
    
    driver = webdriver.PhantomJS(service_args=["--load-images=no"])
    
    #options = Options()
    #chrome_options = webdriver.ChromeOptions()
    #logger.info('00000')
    #options.add_argument('headless')
    #chrome_options.add_argument('headless')
    #logger.info('11111')
    # options.headless = True
    #driver = webdriver.Chrome(chrome_options=chrome_options)
    #driver = webdriver.Firefox(options=options)
    logger.info('driver created.')
    wait = WebDriverWait(driver, 10)
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='باز کردن سایت')
        driver.get("http://sada.guilan.ac.ir/SubSystem/Edari/PRelate/Site/SignIn.aspx")
        if 'sada.guilan.ac.ir/GoToDashboard.aspx' in driver.current_url:
            logger.info('ey baba???????????????????????????')
            driver.find_element_by_class_name('refreshDash').click()
            # elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'ورود به س')))
            elem = wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
            elem.click()
            elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_040101')))
            driver.get(elem.get_property('src'))
        
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='ورود به سامانه')
        elem = driver.find_element_by_name('SSMUsername_txt')
        elem.send_keys(user_data['username'])

        elem = driver.find_element_by_name('SSMPassword_txt')
        elem.send_keys(user_data['password'])
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='وارد شدن با یوزرنیم و پسورد')
        elem.send_keys(Keys.ENTER)
        sleep(0.75)
        elem = wait.until(ec.presence_of_element_located((By.ID, 'Default_URL_TAB_ID')))
        elem = elem.find_element_by_class_name('close')
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'userInfoTitle')))

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='رفتن به قسمت امور آموزش')
        elem.click()
        # elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'امور آموزش')))
        elem = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@onclick="onMenuItemClick(this,\'0202\',\'None\');"]')))
        elem.click()
        
        '''
        elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'کارنامه ترم')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_020205')))
        driver.get(elem.get_property('src'))
        
        sel = Select(wait.until(ec.presence_of_element_located((By.ID, 'Term_Drp'))))
        sel.select_by_index(len(sel.options) - 1)
        elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'انتخاب واحد')))
        elem.click()
        sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        user_data['first_info'] = []
        user_data['midterm'] = []
        user_data['exams'] = []
        gt = soup.find(id='mxgrid_container')
        table = gt.find('table', class_='mxgrid ')
        rows = table.find_all('tr')
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            user_data['first_info'].append(
                parts_of_row[time_column_index].text + '\t\t\t' + parts_of_row[1].text +
                '\t\t(((' + parts_of_row[time_column_index - 1].text.replace('\n ', ''))
        '''

        time_column_index = 11
        gc.collect()
        # elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'فرم تثب')))
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='رفتن به قسمت فرم تثبیت انتخاب واحد')
        elem = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@onclick="onMenuItemClick(this,\'020203\',\'Tab\');"]')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_020203')))
        driver.get(elem.get_property('src'))
        time_column_index = 11
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='استخراج اطلاعات از سایت')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        rows = soup.find_all('table', class_='grd')
        del soup
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

        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='پردازش روی اطلاعات بدست اومده')
        text_process.main(user_data, chat_id)
        gc.collect()
        bot.edit_message_text(chat_id=chat_id, message_id=sent_message, text='ساختن تصویر برنامه')
        pr = Process(target=time_table_file.main, args=(user_data, chat_id, True))
        pr.daemon = True
        pr.start()
        pr.join()

        # time_table_file.main(user_data, bot, update, from_scrp=True)
        
    except TimeoutException:
        bot.send_message(chat_id=chat_id, text='بازم ارور🤦‍♂️' + ' نمیدونم مشکل چیه. میتونی دوباره تست کنی اگه بازم درست نشد به این آیدی یه پیغام بفرست: @ArmanG98 🙏', reply_markup=markup)
        logger.info('selenium common exceptions  || TimeoutException  ||')
        try:
            driver.quit()
            logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        except Exception as e:
            logger.warning(str(e.args))
            pass
    
    except ProtocolError:
        bot.send_message(chat_id=chat_id,
                        text='خب مشکل از سمت منه. در واقع چون سرور مجانیه و ضعیف, حافظه رم پر شده. چند دقیقه دیگه دوباره تست کن اگه درست نشد به این آیدی یه پیغام بفرست: @ArmanG98 🙏' + ' یا اینکه فرم تثبیت انتخاب واحدت کار نمیکنه!',
                        reply_markup=markup)
        #from config import CHAT_ID_OF_ADMIN
        #bot.send_message(chat_id=CHAT_ID_OF_ADMIN, text='سرور رو درست کن داش', reply_markup=markup)
        logger.info(' || ProtocolError  ||')
        try:
            driver.quit()
            logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        except Exception as e:
            logger.warning(str(e.args))
            pass
    
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='بازم ارور🤦‍♂️' + ' نمیدونم مشکل چیه. میتونی دوباره تست کنی اگه بازم درست نشد به این آیدی یه پیغام بفرست: @ArmanG98 🙏', reply_markup=markup)
        logger.warning(str(e.args))
        
        try:
            driver.quit()
            logger.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        except Exception as e2:
            logger.info(str(e2.args))
            pass
