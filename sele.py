import setup
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import time



class FinancailStatement(setup.Setup):
    def __init__(self):
        super().__init__('Selenium',source="VS")
        # self.link = "https://www.buffett-code.com/company/5486/library"
    
    def get_data(self, link):
        self.driver.get(link)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        self.driver.close()
        self.driver.quit()
        return soup
    
    def get_table(self,soup = "", link = "https://www.buffett-code.com/company/5486/library"):
        if soup == "":
            soup = self.get_data(link)
            arr = soup.find_all('a')
            for i in arr:
                if i["href"].find("/company") != -1:
                    print(i["href"])

        else:
            soup = BeautifulSoup(soup,'html.parser',from_encoding='utf-8')
        table = soup.find_all('table')
        table = pd.read_html(str(table))[9]
        return table
    
    def get_pdf_link(self,link_):
        print(link_)
        self.driver.get(link_)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        arr = soup.find_all('a')
        for i in arr:
            if i["href"].find("pdf") != -1:
                return i["href"]
        return ""

F = FinancailStatement()
# table = F.get_table()
link = "https://www.buffett-code.com/company/5486/library/77a40925850ada08b51fba/preview"
link = F.get_pdf_link(link)
print(link)