from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time, os
import pandas as pd
import numpy as np

class Morningstar():

    def __init__(self, 
                 path_download = 'A:\Phong\Crawl_buffett\Financial',
                 email = 'quynhtranga1k2000@gmail.com',
                 password = 'Trang0987145288'): 
        
        self.EMAIL = email
        self.PASSWORD = password
        self.PATH = path_download.replace('Financial','Download')
        self.PATH_SAVE = path_download
        os.makedirs(path_download, exist_ok=True)
        os.makedirs(self.PATH, exist_ok=True)
        self.setDriver()
        self.login()

    def setDriver(self):
        options = Options()
        options.add_experimental_option("prefs", {"download.default_directory": self.PATH})
        self.driver = webdriver.Edge(options=options)
        self.driver.maximize_window()

    def login(self):
        url_login = 'https://www.morningstar.com/stocks/xber/096/financials'
        self.driver.get(url_login)
        time.sleep(2)
        self.driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[1]/div/header/div/div[3]/section/ul/li[3]/a').click() # Find element sign in
        time.sleep(10) # wait for login
        self.driver.find_element(By.ID, 'emailInput').send_keys(self.EMAIL) # Find element email
        self.driver.find_element(By.ID, 'passwordInput').send_keys(self.PASSWORD) # Find element password 
        self.driver.find_element(By.XPATH, '//*[@id="mds-page-shell-content"]/section/div/div[2]/div/div/form/div/button[2]').click() # Click to sign in 
        time.sleep(10)

    def getFinancialSymbols(self, symbol):
        url = f'https://www.morningstar.com/stocks/xber/{symbol}/financials'
        self.driver.get(url)
        time.sleep(2)

        # show all
        self.driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div/div[2]/div[2]/div/div/a/span[2]').click()
        time.sleep(3)

        # download income statement
        self.driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div[2]/button').click()
        # time.sleep(10)
        # os.rename(f'{self.PATH}/Income Statement_Annual_As Originally Reported.xls', f'{self.PATH}/{symbol}_income.csv')

        # balance sheet
        self.driver.find_element(By.XPATH, '//*[@id="balanceSheet"]').click()
        time.sleep(3)

        # download balance sheet
        self.driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div/div[2]/div[3]/div/main/div/div/div[1]/section/sal-components/div/sal-components-stocks-financials/div/div/div/div/div/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div/div[2]/div[2]/div[2]/button').click()
        # time.sleep(10)
        # os.rename(f'{self.PATH}/Balance Sheet_Annual_As Originally Reported.xls', f'{self.PATH}/{symbol}_balance.csv')

    def run(self, path_symbol = 'docs\ListCom_Germany.xlsx'):

        df = pd.read_excel(path_symbol)
        if 'check' not in df.columns: # create column if not exist
            df['check'] = np.nan

        for id in df.index:
            symbol = df['Abbreviation'][id] # get symbol
            check = df['check'][id] # get check
            if check == 'Done':
                continue
            try:
                self.getFinancialSymbols(symbol)
                df['check'][id] = 'Done'
                print(symbol, 'done')
            except Exception as e:
                df['check'][id] = e
                print(symbol, e)

            self.moveToFolder()
            df.to_excel(path_symbol, index=False)

    def moveToFolder(self,):
        lt_ = os.listdir(f'{self.PATH}')
        for i in lt_:
            print(i)
            xls = pd.ExcelFile(f'{self.PATH}\{i}')
            sheetX = xls.parse(0)
            str1 = list(sheetX.columns)[0]
            re = str1[0:str1.find('-')]
            sheetX.to_csv(f'{self.PATH_SAVE}\{re}.csv', index = False)
