# -*- coding: utf-8 -*-
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from bs4 import BeautifulSoup
import text_process
import time_table_file
from telegram import ReplyKeyboardMarkup


reply_keyboard = [['فرستادن نام کاربری و کلمه عبور (username, password)'],
                  ['گرفتن برنامه از erp'],
                  ['ویرایش برنامه', 'گرفتن برنامه ویرایش شده']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def main(user_data, bot, update):
    driver = webdriver.PhantomJS()
    try:
        driver.get("http://erp.guilan.ac.ir")
        if 'erp.guilan.ac.ir/GoToDashboard.aspx' in driver.current_url:
            driver.find_element_by_class_name('refreshDash').click()
        elem = driver.find_element_by_partial_link_text('ورود به س')
        elem.click()
        
        
        
        wait = WebDriverWait(driver, 10)
        elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'ورود به س')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_040101')))

        driver.get(elem.get_property('src'))
        elem = driver.find_element_by_name('SSMUsername_txt')
        elem.send_keys(user_data['username'])

        elem = driver.find_element_by_name('SSMPassword_txt')
        elem.send_keys(user_data['password'] + Keys.ENTER)
        elem = wait.until(ec.presence_of_element_located((By.ID, 'userInfoTitle')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'امور آموزش')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'فرم تثب')))
        elem.click()
        elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_020203')))
        driver.get(elem.get_property('src'))
        time_column_index = 11

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
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
        rows = rows[0:number_of_rows + 1]
        user_data['first_info'] = []
        user_data['midterm'] = []
        for row_index in range(len(rows)):
            parts_of_row = rows[row_index].find_all('td')
            user_data['first_info'].append(
                parts_of_row[time_column_index].find('span').text + '\t\t\t' + parts_of_row[2].find('span').text +
                '\t\t(((' + parts_of_row[time_column_index - 1].find(
                    'span').text.replace('\n ', ''))
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
        time_table_file.main(user_data, bot, update, from_scrp=True)
        
    except selenium.common.exceptions.TimeoutException:
        print('selenium.common.exceptions.TimeoutException')
        print(user_data)
        bot.send_message(chat_id=update.message.chat_id,
                         text='نمیدونم مشکل از تو بود یا سایت یا من؟! ولی محض اطمینان یه بار دیگه یوزر و پسوردتو درست '
                              'بفرست اگه نتونستم که دیگه شرمنده.', reply_markup=markup)
        driver.close()
    except Exception as e:
        print(e.args)
        print(user_data)
        bot.send_message(chat_id=update.message.chat_id,
                         text='نمیدونم مشکل از تو بود یا سایت یا من؟! ولی محض اطمینان یه بار دیگه یوزر و پسوردتو درست '
                              'بفرست اگه نتونستم که دیگه شرمنده.', reply_markup=markup)
        try:
            driver.close()
        except Exception as e:
            print(e.args)
            pass
