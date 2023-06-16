import os, time, subprocess
import pandas as pd
import numpy as np
import warnings
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from logs.log_setup import *
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
warnings.simplefilter("ignore", UserWarning)

from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

class GetPDF:
    def __init__(
        self,
        path_all_com="Crawl/buffett/docs/List_company_23052023 - Listing.csv",
        path_save="SAVE/Buffett/Data",
        time_sleep: int = 30,
        browser_name: str = "Chrome",
        headless: bool = False,
        tor_path = r"A:\Tor Browser"
    ):
        self.tor_path = tor_path
        if browser_name == 'PC':
            self.first_tor_setup()
        self.browser_name = browser_name
        self.headless = headless
        self.setup_driver()
        self.path_company = "https://www.buffett-code.com/company"
        self.path_save = path_save
        self.path_all_com = path_all_com
        self.log_path = self.path_all_com.replace(".csv", ".log").replace(
            "docs/", "logs/"
        )
        self.time_sleep = time_sleep

    def first_tor_setup(self):
        profile_path = os.path.expandvars(
            self.tor_path + r"\Browser\TorBrowser\Data\Browser\profile.default"
        )
        options = Options()
        options.set_preference("profile", profile_path)
        service = Service(
            executable_path=GeckoDriverManager().install()
        )

        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.socks", "127.0.0.1")
        options.set_preference("network.proxy.socks_port", 9050)
        options.set_preference("network.proxy.socks_remote_dns", False)

        tor_exe = subprocess.Popen(
            os.path.expandvars(
                self.tor_path + r"\Browser\TorBrowser\Tor\tor.exe"
            )
        )
        # tor_exe.kill()
        driver = Firefox(service=service, options=options)
        driver.get("https://check.torproject.org")
        time.sleep(1)


    def reset_driver(self):
        """
        Reset driver
        """
        self.driver.quit()
        self.setup_driver()

    def setup_driver(self):
        """
        Setup driver
        """
        if self.browser_name == 'Chrome': # Chrome
            # tor_proxy = "127.0.0.1:9050"
            chrome_options = Options()
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument(
                "--user-data=C:\\Users\\ADMIN\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
            )
            # chrome_options.add_argument("--proxy-server=socks5://%s" % tor_proxy)
            self.driver = webdriver.Chrome(options=chrome_options)

        if self.browser_name == 'Firefox': # Firefox
            option = webdriver.FirefoxOptions()
            option.binary_location = r'/Applications/Tor Browser.app/Contents/MacOS/firefox'
            browser = webdriver.Firefox(options=option)
            self.driver = browser
            time.sleep(3)
            self.driver.find_element('id', 'connectButton').click()
            time.sleep(10)
            self.driver.get("https://check.torproject.org")

        if self.browser_name == 'PC': # Use tor in windows
            profile_path = os.path.expandvars(
                self.tor_path + r"\Browser\TorBrowser\Data\Browser\profile.default"
            )

            options=Options()
            options.headless = self.headless
            options.set_preference('profile', profile_path)
            service = Service(
                executable_path=GeckoDriverManager().install()
            )
            options.binary_location = self.tor_path + r"\Browser\firefox.exe"
            options.set_preference('network.proxy.type', 1)
            options.set_preference('network.proxy.socks', '127.0.0.1')
            options.set_preference('network.proxy.socks_port', 9050)

            self.driver = Firefox(service=service, options=options)
            self.driver.get("https://check.torproject.org")

        # self.driver.get("https://www.buffett-code.com/")
        # soup = BeautifulSoup(
        #     self.driver.page_source, "html.parser", from_encoding="utf-8"
        # )
        # if self.check_error(soup):
        #     self.driver.quit()
        #     print('-----------------------')
        #     return self.setup_driver()
        return ''


    def get_data(self, link):
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
    
    def check_error(self, soup):
        """
        Check error
        Input: BeautifulSoup of https://www.buffett-code.com/
        Output: True if error else False
        """
        time.sleep(1)
        if '403 Forbidden' in soup.text or 'アクセスを一時的に制限しています。' in soup.text:
            print('Lỗi rồi reset lại đi')
            self.reset_driver()
            return True
        return False
        
    def get_table(self, id_company=5486):
        """
        Get table have link pdf in web
        Input: BeautifulSoup of company
        Output: table have link pdf in web
        """
        print(f"{self.path_company}/{id_company}/library")
        soup = self.get_data(f"{self.path_company}/{id_company}/library")
        table = soup.find_all("table")
        if self.check_error(soup):
            return self.get_table(id_company)
        return table

    def get_pdf_link(self, link_):
        """
        Get download link pdf in web
        Input: link preview pdf file
        Output: link download pdf file
        """
        self.driver.get(link_)
        soup = BeautifulSoup(
            self.driver.page_source, "html.parser", from_encoding="utf-8"
        )
        arr = soup.find_all("a")
        for i in arr:
            if i["href"].find("pdf") != -1:
                return i["href"]
        if self.check_error(soup):
            return self.get_pdf_link(link_)
        return ""

    def create_link_df(self, table):
        """
        Create DataFrame have link pdf
        Input: table have information of link pdf
        Output: DataFrame have link pdf
        """
        json_company = {}
        for id_year, tr_year in enumerate(table[0].find_all("tr")):
            json_company_quy = {}
            year = ""
            for id_quy, td_quy in enumerate(tr_year.find_all("td")):
                lst_text, lst_link = [], []
                for li in td_quy.find_all("li"):
                    if "決算短信" in li.text:
                        lst_text.append(li.text)
                        lst_link.append(
                            f"https://www.buffett-code.com{li.find('a')['href']}"
                        )
                if id_quy != 0 and id_quy != 5:
                    json_company_quy[f"Time_Q{id_quy}"] = lst_text
                    json_company_quy[f"Link_Q{id_quy}"] = lst_link
                    json_company_quy[f"Link_pdf_Q{id_quy}"] = np.nan
                if td_quy["class"][0] == "center":
                    year = td_quy.text
            if year != "":
                json_company[year] = json_company_quy.copy()

        df = pd.DataFrame(json_company).T.reset_index(drop=False)
        return df.rename(columns={"index": "Year"})

    def make_folder(self, id_company: int):
        """
        Make folder to save pdf
        Input: id company
        Output: None
        """
        try:
            os.makedirs(f"{self.path_save}/{id_company}")
            os.makedirs(f"{self.path_save}/{id_company}/PDF")
            os.makedirs(f"{self.path_save}/{id_company}/docs")
        except:
            pass

    def save_check_point(self, id_company: int):
        """
        Save check point to checklist file
        Input: id company
        Output: None
        """
        if not os.path.exists(f"{self.path_save}/{id_company}/docs/link.csv"):
            table = self.get_table(id_company=id_company)
            df = self.create_link_df(table)
            df.to_csv(f"{self.path_save}/{id_company}/docs/link.csv", index=False)
            df_check = df.copy()
            for quy in ["Q1", "Q2", "Q3", "Q4"]:
                df_check[f"download_{quy}"] = np.nan
            df_check.to_csv(
                f"{self.path_save}/{id_company}/docs/check.csv", index=False
            )
        else:
            df = pd.read_csv(f"{self.path_save}/{id_company}/docs/link.csv")
            for quy in ["Q1", "Q2", "Q3", "Q4"]:
                df[f"Time_{quy}"] = df[f"Time_{quy}"].apply(lambda x: eval(x))
                df[f"Link_{quy}"] = df[f"Link_{quy}"].apply(lambda x: eval(x))
        self.df_company = df
        return df

    def save_pdf_by_requests(self, path_save_pdf, link_pdf):
        """
        Download pdf file from link pdf
        Input: path to save pdf file, link pdf file
        Output: None
        """

        response = requests.get(link_pdf)
        with open(path_save_pdf,"wb") as f:
            f.write(response.content)
        
    def get_download_pdf(self, id_company: int):
        """
        Download pdf file from link pdf
        Input: id company
        Output: None
        """
        df = self.df_company
        df_check = pd.read_csv(f"{self.path_save}/{id_company}/docs/check.csv")

        for quy in ["Q1", "Q2", "Q3", "Q4"]:
            for id in df.index:
                if pd.isna(df_check[f"download_{quy}"][id]):
                    for id_link in range(len(df[f"Time_{quy}"][id])):
                        year_ = df[f"Year"][id]
                        link_preview = df[f"Link_{quy}"][id][id_link]
                        if not f"{self.path_company}" in link_preview:
                            msg = "Nan"
                        else:
                            try:
                                link_pdf = self.get_pdf_link(link_preview)
                                name = df[f"Time_{quy}"][id][id_link].replace(" ", "").replace("/", "_")
                                path_save_pdf = f"{self.path_save}/{id_company}/PDF/{year_}_{quy}_{name}.pdf"
                                self.save_pdf_by_requests(path_save_pdf, link_pdf)
                                msg = "OK"
                            except:
                                msg = None
                        print(
                            f"{self.path_save}/{id_company} - {year_} - {quy} - {id_link} - {msg} - {link_preview}"
                        )
                        df_check[f"download_{quy}"][id] = msg
                        df_check.to_csv(
                            f"{self.path_save}/{id_company}/docs/check.csv", index=False
                        )
                        time.sleep(self.time_sleep)

    def save_pdf(self, id_company: int):
        """
        Save pdf
        Input: id company
        Output: None
        """
        start = time.time()
        self.make_folder(id_company)
        self.save_check_point(id_company)
        self.get_download_pdf(id_company)
        end = time.time()
        print(f"Time run {id_company}: {end - start}")

    def get_all_com(self, reverse: bool = False):
        """
        Get all company
        """
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
                    self.save_pdf(id_company=id_company)
                    msg = "Done"
                    log_message(f"Successfully: ID {id_company}")
                except:
                    msg = "False"
                    log_message(f"Failed: ID {id_company}")
                lst_com["check"][i] = msg
                lst_com.sort_index(inplace=True)
                lst_com.to_csv(self.path_all_com, index=False)
