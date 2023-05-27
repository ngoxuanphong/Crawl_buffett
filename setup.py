from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import requests
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
# from Crawl.base.URL import URL_VIETSTOCK, USER,PASSWORD
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
pd.set_option('mode.chained_assignment', None)

class Setup():
    def __init__(self,type_tech = "Selenium",source="CF") -> None:
        # self.user = USER
        # self.password = PASSWORD
        self.year = 0
        self.quater = 0
        self.day = 0
        self.symbol = ""
        self.form_data = {}
        # self.VS = URL_VIETSTOCK["LOGIN"]
        self.HEADERS = {'content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla'}
        if type_tech == "Selenium":
            self.reset_driver(source = source)
        elif type_tech == "Colab":
            self.reset_colab()
        else:
            pass
        if type_tech == "Selenium":
            try:
                self.reset_colab()
            except:
                self.reset_driver(source = source)
    def turn_off_drive(self):
        try:
            self.driver.quit()
        except:
            pass
        
    def reset_colab(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('enable-automation')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome('chromedriver',chrome_options=chrome_options)

    def reset_driver(self, path="chromedriver.exe",source="CF"):
        chrome_options = webdriver.ChromeOptions()
        if source=="CF":
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('enable-automation')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-browser-side-navigation')
            chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(executable_path=path,chrome_options=chrome_options)

    def request_link(self,link,time=5):
        try:
            self.driver.set_page_load_timeout(time)
            self.driver.get(link)
        except:
            self.driver.quit()
            # try:
            #     self.reset_colab()
            # except:
            #     self.reset_driver()
            # self.request_link(link,10)
            # pass 

    def format(self, time):
        s = time.split("-")
        self.year = int(s[0])
        self.quater = int(s[1])//3+1
        self.day = int(s[2])
        return self.year, self.quater

    def find_element_by_xpath(self,something):
        try:
          element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,something)))
        finally:
            pass
        return element
    def find_element_by_other(self,something,other):
        try:
          element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((other,something)))
        finally:
            pass
        return element

    def click_something_by_xpath(self, something):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, something))
            )
            element.click()
        except:
            # self.driver.refresh()
            pass

    def click_something_by_id(self, something):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, something))
            )
            element.click()
        except:
            self.driver.refresh()
            pass
    
    def click_something_by_other(self, something,other):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((other, something))
            )
            element.click()
        except:
            self.driver.refresh()
            pass
    def send_something_by_id(self,id,somthing):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, id))
            )
            element.clear()
            element.send_keys(somthing)
        except:
            # self.driver.refresh()
            pass
    def send_something_by_other(self,somthing,other_txt,other):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((other, other_txt))
            )
            element.click()
            element.clear()
            element.send_keys(somthing)
        except:
            # self.driver.refresh()
            pass
    
    def r_get(self,url):
        return requests.get(url, headers = self.HEADERS)
    
    def r_post(self,url,data,cookie={}, headers = {}):
        return requests.post(url, headers = headers,data = data, cookies=cookie)

    def click_select(self,name,value):
        select = Select(self.driver.find_element(By.NAME,name))
        select.select_by_value(value)
        

    def download_batch_get_post(self,url,dict_={}):
        rs = requests.post(url, data = self.form_data, headers = self.HEADERS)
        soup = BeautifulSoup(rs.content, 'html.parser')
        table = soup.find('table',dict_)
        stock_slice_batch = pd.read_html(str(table))[0]
        return stock_slice_batch
    
    def download_batch_selenium(self,url,dict_={}):
        self.request_link(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        table = soup.find('table',dict_)
        stock_slice_batch = pd.read_html(str(table))[0]
        return stock_slice_batch

    def download_batch_get_request(self,url,dict_={}):
        rs = requests.get(url, headers = self.HEADERS)
        soup = BeautifulSoup(rs.content, 'html.parser')
        table = soup.find_all('table',dict_)
        stock_slice_batch = pd.read_html(str(table))[0]
        return stock_slice_batch
    
    def login_VS(self):
        self.driver.get(self.VS)
        self.driver.maximize_window() 
        try:       
            self.click_something_by_id('btn-request-call-login')
            self.send_something_by_id('txtEmailLogin',self.user)
            self.send_something_by_id('txtPassword',self.password)
            self.click_something_by_id('btnLoginAccount')
        finally:
            time.sleep(10)
            pass
    
    def checkstatus_TVSI(self,link):
        rs = requests.get(link)
        soup = BeautifulSoup(rs.content, 'html.parser')
        list_ = soup.find_all("div",{"class":"container"})
        if len(list_) == 0:
            return True
        else:
            return False

