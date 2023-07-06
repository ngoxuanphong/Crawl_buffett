import os, time, subprocess, re
import pandas as pd
import numpy as np
import warnings
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from logs.setup import *
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
warnings.simplefilter("ignore", UserWarning)

from pandas.errors import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)



class GetProxyDriver:
    def __init__(self, 
                 thread_num: int = 3):
        self.thread_num = thread_num
        self.urls = [
                    'https://www.proxynova.com/proxy-server-list/country-vn',
                    'https://www.proxynova.com/proxy-server-list/',
                    'https://www.proxynova.com/proxy-server-list/country-cn',
                    'https://www.proxynova.com/proxy-server-list/country-th/',
                    ]
        self.df_proxy = self.getProxyTable()

    def getProxyTable(self):
        driver = webdriver.Chrome()
        driver.get(np.random.choice(self.urls))

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find('table', id='tbl_proxy_list')
        tbody = tables.find('tbody')

        pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        ip_address = re.findall(pattern, tbody.text)

        df_proxy = pd.read_html(str(tables))[0].dropna(how = 'all')
        df_proxy['Proxy IP'][:len(ip_address)] = ip_address
        driver.quit()
        return df_proxy

    def checkDriver(self, PROXY):
        """
        Check if the driver can access to the website
        
        Parameters
        ----------
        PROXY : str
            Proxy IP and port
            
        Returns
        -------
        chrome : selenium.webdriver.chrome.webdriver.WebDriver
            Chrome driver
        """
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        chrome = webdriver.Chrome(options=chrome_options)
        chrome.implicitly_wait(7)
        chrome.get('https://www.buffett-code.com/')

        if ('バフェット・コード' in chrome.page_source) and ("403 Forbidden" not in chrome.page_source):
            # print('OK')
            return chrome
        else:
            # print('NG')
            chrome.close()

    def getLstDriver(self): # len_proxy: number of proxy
        """
        Get list of chrome driver

        Returns
        -------
        lst_driver : list
            List of chrome driver
        """
        lst_driver= []
        for j in range(int(len(self.df_proxy)/2)):
            i = np.random.choice(list(self.df_proxy.index))
            proxy = self.df_proxy.loc[i, 'Proxy IP']
            port = int(self.df_proxy.loc[i, 'Proxy Port'])
            PROXY = f"{proxy}:{port}"
            # print(PROXY, end = ' -- ')
            try:
                chrome_driver = self.checkDriver(PROXY)
            except:
                # print('Error')
                continue
            if chrome_driver == None:
                continue
            else:
                lst_driver.append(chrome_driver)
            if len(lst_driver) == self.thread_num:
                break
        return lst_driver
    
    def getListDriver(self, ): # len_proxy: number of proxy
        """
        Get list of chrome driver

        Returns
        -------
        lst_driver : list
            List of chrome driver
        """

        lst_driver = self.getLstDriver()
        while len(lst_driver) < self.thread_num:
            self.df_proxy = self.getProxyTable()
            lst_driver += self.getLstDriver()
        return lst_driver

class GetPDF:
    def __init__(
        self,
        path_all_com="Crawl/buffett/docs/List_company_23052023 - Listing.csv",
        path_save="SAVE/Buffett/Data",
        time_sleep: int = 30,
        browser_name: str = "Chrome",
        headless: bool = False,
        tor_path=r"A:\Tor Browser",
    ):
        """
        Parameters
        ----------
        path_all_com : str, optional
            Path to file list all company, by default "Crawl/buffett/docs/List_company_23052023 - Listing.csv"
        path_save : str, optional
            Path to save data, by default "SAVE/Buffett/Data"
        time_sleep : int, optional
            Time sleep to download pdf, by default 30
        browser_name : str, optional
            Browser name ['Chrome', 'Firefox', 'PC'], by default "Chrome"
        headless : bool, optional
            Bool open browser, by default False
        tor_path : str, optional
            Path to tor if use browser_name = 'PC', by default r"A:\Tor Browser"
        """
        self.tor_path = tor_path
        if browser_name == "PC":
            self.setFirstTor()
        self.browser_name = browser_name
        self.headless = headless
        self.get_proxy_driver = GetProxyDriver(thread_num=1)
        self.setDriver()
        self.path_company = "https://www.buffett-code.com/company"
        self.path_save = path_save
        self.path_all_com = path_all_com
        self.log_path = self.path_all_com.replace(".csv", ".log").replace(
            "docs/", "logs/"
        )
        self.time_sleep = time_sleep

    def setFirstTor(self):
        profile_path = os.path.expandvars(
            self.tor_path + r"\Browser\TorBrowser\Data\Browser\profile.default"
        )
        options = Options()
        options.set_preference("profile", profile_path)
        service = Service(executable_path=GeckoDriverManager().install())

        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", 9050)
        options.set_preference("network.proxy.socks_remote_dns", False)

        tor_exe = subprocess.Popen(
            os.path.expandvars(self.tor_path + r"\Browser\TorBrowser\Tor\tor.exe")
        )

        driver = Firefox(service=service, options=options)
        driver.get("https://check.torproject.org")
        time.sleep(1)

    def resetDriver(self):
        """
        Reset driver
        """
        self.driver.quit()
        self.setDriver()


    def setDriver(self):
        """
        Setup driver
        """
        if self.browser_name == "Chrome":  # Chrome
            # tor_proxy = "127.0.0.1:9050"
            from selenium.webdriver.chrome.options import Options
            options = Options()
            # if self.headless:
            #     options.add_argument('--headless')
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("disable-infobars")
            options.add_argument(
                "--user-data=C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
            )
            # options.add_argument("--proxy-server=socks5://%s" % tor_proxy)
            self.driver = webdriver.Chrome(options=options)

        if self.browser_name == "Firefox":  # Firefox
            option = webdriver.FirefoxOptions()
            option.binary_location = (
                r"/Applications/Tor Browser.app/Contents/MacOS/firefox"
            )
            browser = webdriver.Firefox(options=option)
            self.driver = browser
            time.sleep(3)
            self.driver.find_element("id", "connectButton").click()
            time.sleep(10)
            self.driver.get("https://check.torproject.org")

        if self.browser_name == "PC":  # Use tor in windows
            profile_path = os.path.expandvars(
                self.tor_path + r"\Browser\TorBrowser\Data\Browser\profile.default"
            )

            options = Options()
            options.headless = self.headless
            options.set_preference("profile", profile_path)
            service = Service(executable_path=GeckoDriverManager().install())
            options.binary_location = self.tor_path + r"\Browser\firefox.exe"
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", "127.0.0.1")
            options.set_preference("network.proxy.socks_port", 9050)

            self.driver = Firefox(service=service, options=options)
            self.driver.get("https://check.torproject.org")

        if self.browser_name == 'Thread':  # Use tor in windows
            self.driver = self.get_proxy_driver.getListDriver()[0]


    def getData(self, link):
        """
        Get data from link of company
        Input: link of company
        Output: BeautifulSoup of company
        """
        self.driver.get(link)
        time.sleep(2)
        soup = BeautifulSoup(
            self.driver.page_source, "html.parser", from_encoding="utf-8"
        )
        return soup

    def checkError(self, soup):
        """
        Check error

        Parameters
        ----------
        soup : BeautifulSoup
            BeautifulSoup of company

        Returns
        -------
        bool
            True if error
        """
        time.sleep(1)
        if (("403 Forbidden" in soup.text) or 
            ("アクセスを一時的に制限しています。" in soup.text) or 
            ("www.buffett-code.com took too long to respond" in soup.text) or 
            ('An application is stopping Chrome from safely connecting to this site' in soup.text) or 
            ('The connection was reset.' in soup.text) or
            ('Checking the connection' in soup.text) or 
            ('No internet' in soup.text) or
            ('This site can’t be reached' in soup.text)
            ):
            print("Lỗi rồi reset lại đi")
            self. resetDriver()
            return True
        return False

    def getTable(self, id_company: int = 5486):
        """
        Get table have link pdf in web

        Parameters
        ----------
        id_company : int, optional
            id of company, by default 5486

        Returns
        -------
        table
            table have link pdf
        """
        print(f"{self.path_company}/{id_company}/library")
        soup = self.getData(f"{self.path_company}/{id_company}/library")
        table = soup.find_all("table")
        if self.checkError(soup):
            return self.getTable(id_company)
        return table

    def getPdfLink(self, link_):
        """
        Get download link pdf in web

        Parameters
        ----------
        link_ : str
            link of company

        Returns
        -------
            link of download pdf
        """
        self.driver.get(link_)
        soup = BeautifulSoup(
            self.driver.page_source, "html.parser", from_encoding="utf-8"
        )
        arr = soup.find_all("a")
        if self.checkError(soup):
            return self.getPdfLink(link_)
        for i in arr:
            if i["href"].find("pdf") != -1:
                return i["href"]
        return ""

    def createLinkDF(self, table):
        """
        Create DataFrame have link pdf

        Parameters
        ----------
        table : table
            table have link pdf

        Returns
        -------
        DataFrame of link pdf
        """
        json_company = {}
        for id_year, tr_year in enumerate(table[0].find_all("tr")):
            json_company_quarter = {}
            year = ""
            for id_quarter, td_quarter in enumerate(tr_year.find_all("td")):
                lst_text, lst_link = [], []
                for li in td_quarter.find_all("li"):
                    if "決算短信" in li.text:
                        lst_text.append(li.text)
                        lst_link.append(
                            f"https://www.buffett-code.com{li.find('a')['href']}"
                        )
                if id_quarter != 0 and id_quarter != 5:
                    json_company_quarter[f"Time_Q{id_quarter}"] = lst_text
                    json_company_quarter[f"Link_Q{id_quarter}"] = lst_link
                    json_company_quarter[f"Link_pdf_Q{id_quarter}"] = np.nan
                if td_quarter["class"][0] == "center":
                    year = td_quarter.text
            if year != "":
                json_company[year] = json_company_quarter.copy()

        df = pd.DataFrame(json_company).T.reset_index(drop=False)
        return df.rename(columns={"index": "Year"})

    def makeFolder(self, id_company: int):
        """
        Make folder to save pdf

        parameters
        ----------
        id_company : int
            id of company

        Returns
        -------
        None
        """
        try:
            os.makedirs(f"{self.path_save}/{id_company}")
            os.makedirs(f"{self.path_save}/{id_company}/PDF")
            os.makedirs(f"{self.path_save}/{id_company}/docs")
        except:
            pass

    def saveCheckPoint(self, id_company: int):
        """
        Save check point to checklist file

        Parameters
        ----------
        id_company : int
            id of company

        Returns
        -------
        None
        """
        if not os.path.exists(
            f"{self.path_save}/{id_company}/docs/link.csv"
        ):  # check if file not exist
            table = self.getTable(id_company=id_company)
            df = self.createLinkDF(table)
            df.to_csv(f"{self.path_save}/{id_company}/docs/link.csv", index=False)
            df_check = df.copy()
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                df_check[f"download_{quarter}"] = np.nan
            df_check.to_csv(
                f"{self.path_save}/{id_company}/docs/check.csv", index=False
            )
        else:  # if file exist
            df = pd.read_csv(
                f"{self.path_save}/{id_company}/docs/link.csv"
            )  # read file
            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                df[f"Time_{quarter}"] = df[f"Time_{quarter}"].apply(
                    lambda x: eval(x)
                )  # convert string to list
                df[f"Link_{quarter}"] = df[f"Link_{quarter}"].apply(
                    lambda x: eval(x)
                )  # convert string to list
        self.df_company = df
        return df

    def requestPDF(self, path_save_pdf, link_pdf):
        """
        Download pdf file from link pdf

        Parameters
        ----------
        path_save_pdf : str
            path to save pdf
        link_pdf : str
            link of pdf

        Returns
        -------
        None
        """

        response = requests.get(link_pdf)
        with open(path_save_pdf, "wb") as f:
            f.write(response.content)

    def getDownloadPDF(self, id_company: int):
        """
        Download pdf file from link pdf

        Parameters
        ----------
        id_company : int
            id of company

        Returns
        -------
        None
        """
        df = self.df_company
        df_check = pd.read_csv(f"{self.path_save}/{id_company}/docs/check.csv")

        for quarter in ["Q1", "Q2", "Q3", "Q4"]:  # loop through quarter
            for id in df.index:
                if pd.isna(df_check[f"download_{quarter}"][id]):
                    for id_link in range(len(df[f"Time_{quarter}"][id])):
                        year_ = df[f"Year"][id]
                        link_preview = df[f"Link_{quarter}"][id][id_link]
                        if not f"{self.path_company}" in link_preview:
                            msg = "Nan"
                        else:
                            try:
                                link_pdf = self.getPdfLink(link_preview)
                                name = (
                                    df[f"Time_{quarter}"][id][id_link]
                                    .replace(" ", "")
                                    .replace("/", "_")
                                )
                                path_save_pdf = f"{self.path_save}/{id_company}/PDF/{year_}_{quarter}_{name}.pdf"
                                self.requestPDF(path_save_pdf, link_pdf)
                                msg = "OK"
                            except:
                                msg = None
                        print(
                            f"{self.path_save}/{id_company} - {year_} - {quarter} - {id_link} - {msg} - {link_preview}"
                        )
                        df_check[f"download_{quarter}"][id] = msg
                        df_check.to_csv(
                            f"{self.path_save}/{id_company}/docs/check.csv", index=False
                        )
                        if self.browser_name == 'PC':
                            self.resetDriver()
                        else:
                            time.sleep(self.time_sleep)

    def savePDF(self, id_company: int):
        """
        Save pdf

        Parameters
        ----------
        id_company : int
            id of company

        Returns
        -------
        None
        """
        start = time.time()
        self.makeFolder(id_company)
        self.saveCheckPoint(id_company)
        self.getDownloadPDF(id_company)
        end = time.time()
        print(f"Time run {id_company}: {end - start}")

    def getSymbolDoing(self, reverse=False):
        """
        Get symbol doing

        Parameters
        ----------
        None

        Returns
        -------
        list
            list of symbol doing
        """
        df = pd.read_csv(self.path_all_com)
        id = df[df["check"] == "Done"].index[1]
        if reverse:
            id = df[df["check"] == 'Done'].index[-1]
        symbol = df["Symbol"][id]
        df.loc[id, "check"] = "Doing"
        df.to_csv(self.path_all_com, index=False)
        print(f"Doing: {symbol}")
        return symbol
    

    def savePDFThread(self, reverse=False):
        """
        Save pdf

        Parameters
        ----------
        id_company : int
            id of company

        Returns
        -------
        None
        """
        try:
            id_company = self.getSymbolDoing(reverse=reverse)
            self.savePDF(id_company = id_company)
            self.savePDF(id_company = id_company)
            msg = 'True'
        except:
            msg = 'False1'

        # find index by value
        df_temp = pd.read_csv(self.path_all_com)
        id = df_temp['Symbol'].tolist().index(id_company)
        df_temp.loc[id, 'check'] = msg
        df_temp.to_csv(self.path_all_com, index=False)

        # self.resetDriver()
        self.savePDFThread(reverse=reverse)


    def getAllCom(self, reverse: bool = False, save_log: bool = True):
        """
        Get all company in japan stock

        Parameters
        ----------
        reverse : bool
            reverse list company

        Returns
        -------
        None
        """
        # self.re_download_all_company()
        logging.basicConfig(filename=self.log_path, level=logging.INFO)
        lst_com = pd.read_csv(self.path_all_com)
        if "check" not in lst_com.columns:
            lst_com["check"] = np.nan
        if reverse:
            lst_com = lst_com[::-1]
        for i in lst_com.index:
            id_company = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if check != "Done":
                try:
                    self.savePDF(id_company=id_company)
                    msg = "Done"
                    logMessage(save_log, f"Successfully: ID {id_company}")
                except:
                    msg = "False"
                    logMessage(save_log, f"Failed: ID {id_company}")

                df_temp = pd.read_csv(self.path_all_com)
                df_temp["check"][i] = msg
                df_temp.to_csv(self.path_all_com, index=False)
            else:
                self.savePDF(id_company=id_company)

    def reDownload(self, id_company: int):
        """
        Re download company

        Parameters
        ----------
        id_company : int
            id of company
            
        Returns
        -------
        None
        """
        self.savePDF(id_company=id_company)

    def reDownloadAllCompany(self):
        """
        Re download all company

        Parameters
        ----------
        None
        Returns
        -------
        None
        """
        lst_com = pd.read_csv(self.path_all_com)
        for i in lst_com.index:  # loop through company
            id_company = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if os.path.exists(f'Data/{id_company}/docs/check.csv'):
                if check == "Done":  # if company is done
                    self.savePDF(id_company=id_company)
                    self.reDownload(id_company=id_company)

    def convertSymbolFile(self):
        df_symbol= pd.read_csv(self.path_all_com)[['Symbol', 'check']]
        for year in range(2000, 2024):
            for quarter in range(1, 5):
                df_symbol[f'Q{quarter}_{year}'] = np.nan
        return df_symbol

    def checkDownload(self, id_company):
        df_com = pd.read_csv(self.path_save + f'/{id_company}/docs/check.csv')
        df_com = df_com[['Year', 'download_Q1', 'download_Q2', 'download_Q3', 'download_Q4']]

        for year in range(2000, 2024):
            if year not in df_com['Year'].values:
                df_com.loc[len(df_com.index)] = [year, np.nan, np.nan, np.nan, np.nan]
        df_com = df_com.sort_values('Year').reset_index(drop=True)
        df_com.drop(columns=['Year'], inplace=True)

        list_data = df_com.to_numpy()
        list_data = list(list_data.flatten())
        list_data = [id_company, 'Done'] + list_data
        return list_data

    def checklistDownloadPDF(self):
        df_symbol = self.convertSymbolFile()
        for i in df_symbol.index:
            if df_symbol.loc[i, 'check'] == 'Done':
                symbol = df_symbol.loc[i, 'Symbol']
                list_data = self.checkDownload(symbol)
                df_symbol.loc[i, :] = list_data
        df_symbol.replace([np.nan, 'OK'], [0, 1], inplace=True)
        df_symbol['check'] = df_symbol.iloc[:, 2:].sum(axis=1)
        df_symbol.loc[-1] = df_symbol.sum(axis=0)
        df_symbol['Symbol'][-1] = 'Total'
        df_symbol.sort_index(inplace=True)
        df_symbol.to_csv('docs/checklistDownloadPDF.csv', index=False)