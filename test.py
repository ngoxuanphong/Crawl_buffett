import setup
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import time



class FinancailStatement(setup.Setup):
    def __init__(self):
        super().__init__('Selenium',source="VS")
    
    def get_data(self, link):
        self.driver.get(link)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        # self.driver.close()
        # self.driver.quit()
        return soup
    
    def get_table(self,soup = "", id_company = 5486):
        if soup == "":
            soup = self.get_data(f"https://www.buffett-code.com/company/{id_company}/library")
        else:
            soup = BeautifulSoup(soup,'html.parser',from_encoding='utf-8')
        table = soup.find_all('table')
        return table
    
    def get_pdf_link(self,link_):
        self.driver.get(link_)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        arr = soup.find_all('a')
        for i in arr:
            if i["href"].find("pdf") != -1:
                return i["href"]
        return ""


F = FinancailStatement()
table = F.get_table(id_company = 5486)
print(table)