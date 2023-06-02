import os, time
import pandas as pd
import numpy as np
import warnings
import requests
# import setup
from selenium import webdriver
from bs4 import BeautifulSoup

warnings.simplefilter("ignore", UserWarning)



class FinancailStatement():
    def __init__(self):
        # super().__init__('Selenium',source="VS")
        self.driver = webdriver.Chrome()
    
    def get_data(self, link):
        self.driver.get(link)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        return soup
    
    def get_table(self,soup = "", id_company = 5486):
        print(f"https://www.buffett-code.com/company/{id_company}/library")
        soup = self.get_data(f"https://www.buffett-code.com/company/{id_company}/library")
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
                json_company_quy[f'Link_pdf_Q{id_quy}'] = np.nan
            if td_quy['class'][0] == 'center':
                year = td_quy.text
        if year != '':
            json_company[year] = json_company_quy.copy()

    df = pd.DataFrame(json_company).T.reset_index(drop=False)
    return df.rename(columns={'index': 'Year'})


def make_folder(id_company):
    try:
        os.mkdir(f'Data/{id_company}')
        os.mkdir(f'Data/{id_company}/PDF')
        os.mkdir(f'Data/{id_company}/docs')
        os.mkdir(f'Data/{id_company}/docx')
        os.mkdir(f'Data/{id_company}/volume')
    except:
        pass


def save_check_point(F, id_company):
    if not os.path.exists(f'Data/{id_company}/docs/link.csv'):
        table = F.get_table(id_company=id_company)
        df = create_link_df(table)
        df.to_csv(f'Data/{id_company}/docs/link.csv', index=False)
        df_check = df.copy()
        for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
            df_check[f'download_{quy}'] = np.nan
        df_check.to_csv(f'Data/{id_company}/docs/check.csv', index=False)
    else:
        df = pd.read_csv(f'Data/{id_company}/docs/link.csv')
        for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
            df[f'Time_{quy}'] = df[f'Time_{quy}'].apply(lambda x: eval(x))
            df[f'Link_{quy}'] = df[f'Link_{quy}'].apply(lambda x: eval(x))
    return df

def get_download_pdf(F, id_company, df):
    df_check = pd.read_csv(f'Data/{id_company}/docs/check.csv')

    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        for id in df.index:
            if pd.isna(df_check[f'download_{quy}'][id]):
                for id_link in range(len(df[f'Time_{quy}'][id])):
                    year_ = df[f'Year'][id]
                    link_preview = df[f'Link_{quy}'][id][id_link]
                    if not 'https://www.buffett-code.com/company' in link_preview:
                        msg = 'Nan'
                    else:
                        try:
                            link_pdf = F.get_pdf_link(link_preview)
                            name = df[f'Time_{quy}'][id][id_link].replace(' ', '').replace('/', '_')
                            response = requests.get(link_pdf)
                            with open(f'Data/{id_company}/PDF/{year_}_{quy}_{name}.pdf', 'wb') as f:
                                f.write(response.content)
                            msg = 'OK'
                        except:
                            msg = None
                    print(f'Data/{id_company} - {year_} - {quy} - {id_link} - {msg} - {link_preview}')
                    df_check[f'download_{quy}'][id] = msg
                    df_check.to_csv(f'Data/{id_company}/docs/check.csv', index=False)
                    time.sleep(30)


def save_pdf(id_company):
    make_folder(id_company)
    F = FinancailStatement()
    df = save_check_point(F, id_company)
    get_download_pdf(F, id_company, df)