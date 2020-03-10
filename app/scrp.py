# -*- coding: utf-8 -*-
import multiprocessing as mp
import selenium.common.exceptions
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
import time_table_file
from telegram import ReplyKeyboardMarkup

import gc
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def main(user_data, bot, update):
    '''
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:8910',
        desired_capabilities=DesiredCapabilities.PHANTOMJS)
    '''
    
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
    try:
        driver.get("http://sada.guilan.ac.ir/Dashboard.aspx")
        if 'sada.guilan.ac.ir/GoToDashboard.aspx' in driver.current_url:
            driver.find_element_by_class_name('refreshDash').click()
        
        
        wait = WebDriverWait(driver, 10)
        # elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'ورود به س')))
        elem = wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_040101')))

        driver.get(elem.get_property('src'))
        elem = driver.find_element_by_name('SSMUsername_txt')
        elem.send_keys(user_data['username'])

        elem = driver.find_element_by_name('SSMPassword_txt')
        elem.send_keys(user_data['password'] + Keys.ENTER)
        
        sleep(1.2)
        elem = wait.until(ec.presence_of_element_located((By.ID, 'Default_URL_TAB_ID')))
        elem = elem.find_element_by_class_name('close')
        elem.click()
        try:
            wait = WebDriverWait(driver, 0.01)
            elem = wait.until(ec.presence_of_element_located((By.ID, 'userInfoTitle')))
        except:
            logger.debug('')
        wait = WebDriverWait(driver, 10)
        elem = wait.until(ec.presence_of_element_located((By.ID, 'userInfoTitle')))

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
        elem = wait.until(ec.presence_of_element_located((By.XPATH, '//*[@onclick="onMenuItemClick(this,\'020203\',\'Tab\');"]')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_020203')))
        driver.get(elem.get_property('src'))
        time_column_index = 11

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
        text_process.main(user_data, bot, update)
        gc.collect()
        pr = mp.Process(target=time_table_file.main, args=(user_data, bot, update, True))
        pr.daemon = True
        pr.start()
        pr.join()

        # time_table_file.main(user_data, bot, update, from_scrp=True)
        
    except selenium.common.exceptions.TimeoutException:
        
        bot.send_message(chat_id=update.message.chat_id,
                         text='نمیدونم مشکل از تو بود یا سایت یا من؟! ولی محض اطمینان یه بار دیگه یوزر و پسوردتو با دستور (فرستادن نام کاربری و کلمه عبور) درست '
                              'بفرست و دوباره تست کن اگه نتونستم که دیگه شرمنده.', reply_markup=markup)
        logging.info('selenium common exceptions  || TimeoutException  ||')
        try:
            driver.quit()
            logging.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        except Exception as e:
            logging.warning(str(e.args))
            pass
    except Exception as e:
        
        bot.send_message(chat_id=update.message.chat_id,
                         text='نمیدونم مشکل از تو بود یا سایت یا من؟! ولی محض اطمینان یه بار دیگه یوزر و پسوردتو با دستور (فرستادن نام کاربری و کلمه عبور) درست '
                              'بفرست و دوباره تست کن اگه نتونستم که دیگه شرمنده.', reply_markup=markup)
        logging.warning(str(e.args))
        
        try:
            driver.quit()
            logging.info(str(user_data['username'] + '  ||  ' + user_data['password']))
        except Exception as e2:
            logging.info(str(e2.args))
            pass
