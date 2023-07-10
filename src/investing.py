from selenium import webdriver
import time, os
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings('ignore')

class Investing():
    def __init__(self, 
                 path_save: str = 'data_1'):
        self.link_investing = 'https://www.investing.com'
        self.link_list_com = 'https://www.investing.com/stock-screener/?sp=country::35|sector::a|industry::a|equityType::a|exchange::20%3EviewData.symbol;'
        self.EMAIL = 'thiensuofclass@gmail.com'
        self.PASSWORD = 'xuanphong2002'
        self.signIn()
        self.URL_BALANCE = 'https://www.investing.com/pro/TSE:SYMBOL/financials/balance_sheet'
        self.URL_INCOME = 'https://www.investing.com/pro/TSE:SYMBOL/financials/income_statement'
        self.path_save = path_save


    def signIn(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.driver.get(self.link_investing)
        element = self.driver.find_element('xpath', '//*[@id="PromoteSignUpPopUp"]/div[2]/i')
        if element.is_displayed():
            element.click()
            time.sleep(2)
            
        self.driver.find_element('xpath', '//*[@id="userAccount"]/div/a[1]').click()
        time.sleep(0.5)
        self.driver.find_element('id', 'loginFormUser_email').send_keys(self.EMAIL)
        time.sleep(0.5)
        self.driver.find_element('id', 'loginForm_password').send_keys(self.PASSWORD)
        time.sleep(0.5)
        self.driver.find_element('xpath', '//*[@id="signup"]/a').click()
        time.sleep(2)
  
    def getDataFrameFinancial(self):
        self.driver.find_element(By.XPATH, '//*[@id="leftColumn"]/div[8]/div[1]/a[1]').click()
        time.sleep(3)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find('div', {'id': 'rrtable'})
        table = pd.read_html(str(table))[0]
        return table

    def makeDirectory(self):
        os.makedirs(f'{self.path_save}/balance', exist_ok=True)
        os.makedirs(f'{self.path_save}/income', exist_ok=True)
        
    def getFinancial(self, 
                     name_company: str = 'apple',
                     symbol:int = 1301):
        symbol = str(symbol)

        # Get balance
        if f'{symbol}.csv' not in self.list_symbol_balance:
            self.driver.get(f'https://www.investing.com{name_company}-balance-sheet')
            df_balance = self.getDataFrameFinancial()
            df_balance.to_csv(f'{self.path_save}/balance/{symbol}.csv', index=False)

        # Get income
        if f'{symbol}.csv' not in self.list_symbol_income:
            self.driver.get(f'https://www.investing.com{name_company}-income-statement')
            df_income = self.getDataFrameFinancial()
            df_income.to_csv(f'{self.path_save}/income/{symbol}.csv', index=False)

    def getFinancialAll(self, path_all_symbol: str = 'docs/data.csv'):
        self.makeDirectory()
        df = pd.read_csv(path_all_symbol)
        self.list_symbol_balance = os.listdir(f'{self.path_save}/balance')
        self.list_symbol_income = os.listdir(f'{self.path_save}/income')
        for id in df.index:
            symbol = df['Symbol'][id]
            name = df['href'][id]
            try:
                self.getFinancial(name_company= name, 
                                  symbol=symbol)
                print(symbol, 'done')
            except Exception as e:
                print(symbol, e)
            

    def getTableAllSymbol(self):
        soup = BeautifulSoup(
            self.driver.page_source, "html.parser", from_encoding="utf-8"
        )
        table = soup.find_all("table")
        for i in range(len(table)):
            df = pd.read_html(str(table[i]))[0]
            if len(df.columns) >= 8:
                # find href
                href = []
                for a in table[i].find_all("a"):
                    if '/equities/' in a["href"]:
                        href.append(a["href"])
                df = df.iloc[:, :6]
                df["href"] = href
                return df
        return None
    
    def getListCompany(self):
        for i in range(1, 1000):
            self.driver.get(self.link_list_com + str(i))
            time.sleep(3)
            df_temp = self.getTableAllSymbol()
            if i == 1:
                df_concat = df_temp
            else:
                df_concat = pd.concat([df_concat, df_temp], axis=0)
                if self.driver.current_url == self.link_list_com + '1':
                    break
            print(i, df_concat.shape)

        df_concat.drop_duplicates(inplace=True)
        df_concat.to_csv('data.csv', index=False)
