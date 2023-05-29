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


def create_link_df(table):
    json_company = {}
    for id_year, tr_year in enumerate(table[0].find_all('tr')):
        json_company_quy = {}
        year = ''
        for id_quy, td_quy in enumerate(tr_year.find_all('td')):
            lst_text, lst_link = [], []
            for li in td_quy.find_all('li'):
                if '決算短信' in li.text:
                    lst_text.append(li.text)
                    lst_link.append(f"https://www.buffett-code.com{li.find('a')['href']}")
            if id_quy != 0 and id_quy != 5:
                json_company_quy[f'Time_Q{id_quy}'] = lst_text
                json_company_quy[f'Link_Q{id_quy}'] = lst_link
            if td_quy['class'][0] == 'center':
                year = td_quy.text
        if year != '':
            json_company[year] = json_company_quy.copy()
    return pd.DataFrame(json_company).T


