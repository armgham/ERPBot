from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

driver = webdriver.PhantomJS()
driver.get("http://sada.guilan.ac.ir/Dashboard.aspx")
wait = WebDriverWait(driver, 10)
elem = wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'title')))
elem.click()
elem = wait.until(ec.presence_of_element_located((By.ID, 'iframe_040101')))
driver.get(elem.get_property('src'))
print('taammaamm')
