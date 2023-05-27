from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--start-maximized')
# chrome_options.add_argument('enable-automation')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--disable-browser-side-navigation')
# chrome_options.add_argument('--disable-gpu')

# path = "C:\web_driver/chromedriver.exe"
# driver = webdriver.Chrome(executable_path=path)
# # driver = webdriver.Chrome(executable_path=path,chrome_options=chrome_options)
# driver.get("http://www.python.org")
# assert "Python" in driver.title
# elem = driver.find_element(By.NAME, "q")
# elem.clear()
# elem.send_keys("pycon")
# elem.send_keys(Keys.RETURN)
# assert "No results found." not in driver.page_source
# driver.close()


# # Set up selemium trươc nhé!!

import setup
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import time
import re



class FinancailStatement(setup.Setup):
    def __init__(self):
        super().__init__('Selenium',source="VS")
        self.link = "https://www.buffett-code.com/company/5486/library"
    
    def get_data(self):
        self.driver.get(self.link)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        self.driver.close()
        self.driver.quit()
        return soup
    
    def get_table(self,soup = ""):
        if soup == "":
            soup = self.get_data()
            arr = soup.find_all('a')
            for i in arr:
                if i["href"].find("/company") != -1:
                    print(i["href"])

        else:
            soup = BeautifulSoup(soup,'html.parser',from_encoding='utf-8')
        table = soup.find_all('table')
        table = pd.read_html(str(table))[9]
        return table
    

FinancailStatement(setup.Setup)