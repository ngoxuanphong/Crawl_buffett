import os, time
import pandas as pd
import numpy as np
import warnings

import requests
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

warnings.simplefilter("ignore", UserWarning)
from pandas.core.common import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)



class FinancailStatement():
    def __init__(self):
        # super().__init__('Selenium',source="VS")
        chrome_options = Options()

        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('enable-automation')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--disable-browser-side-navigation')
        # chrome_options.add_argument('--disable-gpu')

        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
        chrome_options.add_extension("driver/extension_0_4_9_0.crx")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

        stealth(self.driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine")

    
    def get_data(self, link):
        self.driver.get(link)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        return soup
    
    def get_table(self,soup = "", id_company = 5486):
        print(f"https://www.buffett-code.com/company/{id_company}/library")
        soup = self.get_data(f"https://www.buffett-code.com/company/{id_company}/library")
        table = soup.find_all('table')
        return table
    
    def random_position(self):
        x = np.random.randint(-100,100)
        y = np.random.randint(-100,100)
        z = np.random.randint(0,100)
        self.driver.execute_script(f"window.scrollBy(0, {z});")
        actions = ActionChains(self.driver)
        actions.move_by_offset(x,y).perform()
        time.sleep(np.random.randint(0,50)/10)
        actions.click().perform()
        time.sleep(np.random.randint(0,50)/10)


    def get_pdf_link(self,link_):
        # self.random_position()
        self.driver.get(link_)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source,'html.parser',from_encoding='utf-8')
        arr = soup.find_all('a')
        for i in range(np.random.randint(0,5)):
            try:
                self.random_position()
            except:
                pass
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
        check_done_quater = True
        for id in df.index:
            if pd.isna(df_check[f'download_{quy}'][id]):
                for id_link in range(len(df[f'Time_{quy}'][id])):
                    year_ = df[f'Year'][id]
                    link_preview = df[f'Link_{quy}'][id][id_link]
                    if not 'https://www.buffett-code.com/company' in link_preview:
                        msg = 'Nan'
                    else:
                        # try:
                            check_done_quater = False
                            link_pdf = F.get_pdf_link(link_preview)
                            name = df[f'Time_{quy}'][id][id_link].replace(' ', '').replace('/', '_')
                            response = requests.get(link_pdf)
                            with open(f'Data/{id_company}/PDF/{year_}_{quy}_{name}.pdf', 'wb') as f:
                                f.write(response.content)
                            msg = 'OK'
                        # except:
                        #     msg = None
                    print(f'Data/{id_company} - {year_} - {quy} - {id_link} - {msg} - {link_preview}')
                    df_check[f'download_{quy}'][id] = msg
                    df_check.to_csv(f'Data/{id_company}/docs/check.csv', index=False)
                    time.sleep(np.random.randint(1, 5))
        if check_done_quater != True:
            print(f'Finish {quy}')
            time.sleep(100)


def save_pdf(id_company):
    make_folder(id_company)
    F = FinancailStatement()
    df = save_check_point(F, id_company)
    get_download_pdf(F, id_company, df)