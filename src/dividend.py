import tabula, os, re
import pdfplumber
import os
import pandas as pd
import numpy as np
import warnings
from src.ocrpdf import ocrPDF, convertPDFToText
import PyPDF2
import warnings

warnings.simplefilter("ignore", UserWarning)


class GetDividend:
    def __init__(self,
            path_save:str = 'Data',
            ):
        self.path_save = path_save

    def get_dividend_table(self, 
                           tables, 
                           year="Any", 
                           table_id:int = 4):
        df = pd.DataFrame(tables[table_id])
        df.dropna(subset=df.columns[0], inplace=True)
        df.dropna(axis=1, how="all", inplace=True)
        df.columns = np.arange(len(df.columns))
        df.drop(columns=df.columns[5:], inplace=True)
        df.dropna(axis=0, how="all", inplace=True)
        df = df.reset_index(drop=True)
        df = df.iloc[[1]]
        df.columns = [year, "Q1", "Q2", "Q3", "Q4"]
        df[year].iloc[0] = year
        if (pd.isna(df.iloc[0]) == False).all() and (
            df.iloc[0, 1:].str.len() < 10
        ).all():
            return df.reset_index(drop=True)
        raise Exception("Don't have dividend table'")
        
    def get_dividend_table_from_pdf(self, 
                                    id_company : int = 1301,
                                    year: str = '2022', 
                                    quy: str = 'Q4'):
        for file in os.listdir(self.path_save + f"Data/{id_company}/PDF"):
            if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
                file_name = file
                path_of_file = self.path_save + f"Data/{id_company}/PDF/{file_name}"
                try:
                    file_name = file
                    path_of_file = self.path_save + f"Data/{id_company}/PDF/{file_name}"
                    pdf = pdfplumber.open(path_of_file)
                    page = pdf.pages[0]
                    text = page.extract_text()
                    # text = convertPDFToText(path_of_file)
                    text = text.replace(" ", "")
                    df = self.get_dividend_table(tables, year)
                    if len(df.index) == 1:
                        return df
                except:
                    try:
                        ocr_file = path_of_file.replace(".pdf", "_ocr.pdf")
                        if os.path.exists(ocr_file) == False:
                            ocrPDF(path_of_file)
                        tables = tabula.read_pdf(
                            ocr_file, pages="all", multiple_tables=True, silent=True
                        )
                        df = self.get_dividend_table(tables, year)
                        if len(df.index) == 1:
                            return df
                    except:
                        print("This year have the bug", year)
                        try:
                            df = self.get_dividend_table(tables, year, table_id=3)
                            if len(df.index) == 1:
                                return df
                        except:
                            pass
                return pd.DataFrame(
                    {year: year, "Q1": "B", "Q2": "B", "Q3": "B", "Q4": "B"}, index=[0]
                )

        return pd.DataFrame(
            {year: year, "Q1": "N/A", "Q2": "N/A", "Q3": "N/A", "Q4": "N/A"}, index=[0]
        )

    def getDividendTable(self, year, text, text_replace, idx_key):
        """
        Parameters
        ----------
        year : str
        text : str
            Bản gốc đọc từ pdf
        text_replace : str 
            Text bỏ đi các dấu khoảng trắng
        idx_key : int 
            index xác định vị trí mục chứa bảng cần lấy ( index trong text_replace)
        
        Return
        -----------
        DataFrame :
            Dividend cần lấy trong bảng
        """
        num_line = text_replace[: idx_key + 1].count('\n') #Số dòng để tới mục cần tìm
        for _ in range(num_line):
            idx = text.find('\n')
            text = text[idx + 1:] # Hết vòng lặp: text (cuoi cung) là vị trí bắt đầu của mục cần tìm
            
        # print(text)
        num_line1 = text[:text.find('月')].count('\n') # Đếm số dòng
        for _ in range(num_line1 + 1):
            idx = text.find('\n')
            text = text[idx + 1:] # text (cuối cùng) = Dòng cần tìm trong bảng

        text_dvd = text[text.find('期') +2: text.find('\n')].strip() #Dữ liệu chứa dividend cần lấy
        # print(text_dvd)
        lst_dvd = text_dvd.split(" ") #list = dividend + các thông số khác trong dòng đó
        # print(year, lst_dvd)


        # Do cấu trúc bảng khác nhau nên sẽ có nhiều trường hợp tổ chức dữ liệu
        if len(lst_dvd) >= 4 and len(lst_dvd) < 10: #số lượng thông số trong list_dvd
            return pd.DataFrame(
                {year: year, "Q1": lst_dvd[0], "Q2": lst_dvd[1], "Q3": lst_dvd[2], "Q4": lst_dvd[3]}, index=[0]
            )
        elif len(lst_dvd) >= 10: # 
            try:
                check = int(lst_dvd[1]) # try xem có phải là số không
                #Truong hop vi du: ― 1 50 ― 1 50 3 00 857 54.1 1.7
                return pd.DataFrame(
                    {year: year, "Q1": lst_dvd[0],
                                "Q2": lst_dvd[1] + '.' + lst_dvd[2],
                                "Q3": lst_dvd[3],
                                "Q4": lst_dvd[4] + '.' + lst_dvd[5]}, index=[0]
                )
            except:
                try:
                    check = int(lst_dvd[4])
                    #Truong hop vd:  － － － 1 00 1 00 27 △109.9 1.7
                    return pd.DataFrame(
                        {year: year, "Q1": lst_dvd[0],
                                    "Q2": lst_dvd[1],
                                    "Q3": lst_dvd[2],
                                    "Q4": lst_dvd[3] + '.' + lst_dvd[4]}, index=[0]
                    )
                except:
                    #Truong hop vd:  ― ― 1 50 ― ― 1 50 3 00 857 54.1 1.7
                    return pd.DataFrame(
                        {year: year, "Q1": lst_dvd[0] + '.' + lst_dvd[1],
                                    "Q2": lst_dvd[2] + '.' + lst_dvd[3],
                                    "Q3": lst_dvd[4] + '.' + lst_dvd[5],
                                    "Q4": lst_dvd[6] + '.' + lst_dvd[7]}, index=[0]
                    )
                
        return pd.DataFrame({year: year, "Q1": "_", "Q2": "_", "Q3": "_", "Q4": "_"}, index=[0])
        
        # loi dich: 2020453A HA ーー 0.00 — 10.00 10.00 8,804 35.2 1.4--- 9831 2019 q4
        
    def getDividendTableFromPdf(self, 
                                    id_company : int = 1301,
                                    year: str = '2022', 
                                    quy: str = 'Q4'):
        """
        Parameters
        ----------
        id_company : int
            default is 1301
        year : int
            default is '2022'
        quy : int
            default is 'Q4'

        return
        ----------
        DataFrame
            Dividend in 'Q4'
        """
        for file in os.listdir(self.path_save + f"Data/{id_company}/PDF"):
            if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
                try:
                    file_name = file
                    path_of_file = self.path_save + f"Data/{id_company}/PDF/{file_name}"
                    pdf = pdfplumber.open(path_of_file)

                    page = pdf.pages[0]
                    text = page.extract_text() # text này là bản gốc
                    # print(text)
                    text_replace = text.replace(" ", "") # bỏ hết các khoảng cách
                    idx_key = text_replace.find('配当の状況') #Từ khóa xác định phần chưa bảng cần lấy
                    
                    if idx_key != -1:
                        return self.getDividendTable(year, text, text_replace, idx_key)
                    
                    else:# có thể là đọc file lỗi -> đọc lại theo ocr
                        ocr_file = path_of_file.replace(".pdf", "_ocr.pdf")
                        if os.path.exists(ocr_file) == False:
                            ocrPDF(path_of_file)
                        pdf = pdfplumber.open(ocr_file)

                        page = pdf.pages[0]
                        text = page.extract_text() # text này là bản gốc
                        text_replace = text.replace(" ", "") # bỏ hết các khoảng cách
                        idx_key = text_replace.find('配当の状況') #Từ khóa xác định phần chưa bảng cần lấy
                    
                        if idx_key != -1:
                            return self.getDividendTable(year, text, text_replace, idx_key)
                        else: 
                            #vẫn lỗi đọc file, không tìm đc key_word
                            return pd.DataFrame(
                                {year: year, "Q1": "b", "Q2": "b", "Q3": "b", "Q4": "b"}, index=[0]
                            )
                except:
                    return pd.DataFrame(
                                {year: year, "Q1": "B", "Q2": "B", "Q3": "B", "Q4": "B"}, index=[0]
                            )

        return pd.DataFrame(
            {year: year, "Q1": "N/A", "Q2": "N/A", "Q3": "N/A", "Q4": "N/A"}, index=[0]
        )
    
    def getTimeDividend(self, time_text):
        """
        Parameters
        ----------
        time_text : str

        Return
        ----------
        list[str] | 0
            convert time_dividend -> dd_mm_yyyy
        """
        if len(time_text) < 3:
            return 0
        matches = re.findall(r"\d+", time_text)
        if time_text[0] == "平" :
            if time_text[2] == '元' and len(matches) == 2:
                return [
                    f"{int(matches[1])}_{int(matches[0])}_{2019}"
                ]
            if len(matches) == 3:
                return [
                        f"{int(matches[2])}_{int(matches[1])}_{int(matches[0]) + 1988 }"
                    ]
            if len(matches) == 4:
                return [
                        f"{int(matches[3])}_{int(matches[2])}_{int(matches[0])*10 + int(matches[1]) + 1988 }"
                    ]
        if time_text[0] == "令" :
            if time_text[2] == '元' and len(matches) == 2:
                return [
                    f"{int(matches[1])}_{int(matches[0])}_{2019}"
                ]
            if len(matches) == 3:
                return [
                        f"{int(matches[2])}_{int(matches[1])}_{int(matches[0]) + 2018 }"
                    ]
            if len(matches) == 4:
                return [
                        f"{int(matches[3])}_{int(matches[2])}_{int(matches[0])*10 + int(matches[1]) + 1988 }"
                    ]
        if len(matches) == 3:
            if int(matches[0]) > 2000:
                return [f"{int(matches[2])}_{int(matches[1])}_{int(matches[0])}"]
        return 0

    def getDataFromPdf(self, 
                          id_company:int = 1301, 
                          year: str = '2022', 
                          quy: str = 'Q4'):
        """
        Parameters
        ----------
        id_company : int
            id of company default is 1301
        year : str
            year default is '2022'
        quy : str
            default is 'Q4'
        Return
        ---------
        list[str]
            time_dividend
        """
        # print(f'{year}_{quy}')
        try:
            for file in os.listdir(self.path_save + f"Data/{id_company}/PDF"):
                if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
                    file_name = file
                    path_of_file = self.path_save + f"Data/{id_company}/PDF/{file_name}"
                    pdf = pdfplumber.open(path_of_file)
                    page = pdf.pages[0]
                    text = page.extract_text()
                    # text = convertPDFToText(path_of_file)
                    text = text.replace(" ", "")

                    for t in ["配当支払開始予定日", '配支当払開始予定日', '配文当払開始予定日']:
                        idx = text.find(t)
                        if idx != -1:
                            break

                    if idx != -1:
                        text__ = text[idx + 9 : ]
                        time_text = text__[0 : text__.find('\n')]
                        ddmmyyyy = self.getTimeDividend(time_text) #convert -> dd_mm_yyyy
                        if ddmmyyyy:
                            return ddmmyyyy
                        else:
                            return [time_text] # nếu không chuyển đổi đc thì in ra time_dividend chưa qua xử lý
                    else:
                        ocr_file = path_of_file.replace(".pdf", "_ocr.pdf")
                        if os.path.exists(ocr_file) == False:
                            ocrPDF(path_of_file)
                        pdf = pdfplumber.open(ocr_file)

                        page = pdf.pages[0]
                        text = page.extract_text()
                        # text = convertPDFToText(path_of_file)
                        text = text.replace(" ", "")

                        for t in ["配当支払開始予定日", '配支当払開始予定日', '配文当払開始予定日']:
                            idx = text.find(t)
                            if idx != -1:
                                break
                        if idx!= -1:
                            text__ = text[idx + 9 : ]
                            time_text = text__[0 : text__.find('\n')]
                            ddmmyyyy = self.getTimeDividend(time_text)
                            if ddmmyyyy:
                                return ddmmyyyy
                            else:
                                return [time_text] # nếu không chuyển đổi đc thì in ra time_dividend chưa qua xử lý
                            
                    #     if os.path.exists(ocr_file) == False:
                    #         ocrPDF(path_of_file)
                    #     text_ = convertPDFToText(ocr_file)
                    #     print(2, text_) #----------------------------
                    #     text_ = text_.replace(" ", "")

                    #     idx = text_.find("配当支払開始予定日")
                    #     if idx != -1:
                    #         _ = text_.find("四半期報告書提出予定日")
                    #         if text_[_ + 11 : _ + 14] == "\n配当":
                    #             return ["B"]

                    #         time_text = text_[idx + 9 : idx + 20]
                    #         temp = self.get_time_dividend(time_text)
                    #         if temp:
                    #             # print(1)
                    #             return temp

                    #     # case 1:
                    #     idx = text_.find("配当文払開始予定日")
                    #     if idx != -1:
                    #         time_text = text_[idx + 9 : idx + 20]
                    #         temp = self.get_time_dividend(time_text)
                    #         if temp:
                    #             # print(2)
                    #             return temp

                    #     # Case 2:
                    #     if text_.find("配当") != -1:
                    #         idx = text_.find("TEL")
                    #         time_text = text_[idx + 16 : idx + 27]
                    #         temp = self.get_time_dividend(time_text)
                    #         if temp:
                    #             # print(3)
                    #             return temp

                    return ["b"] # không dọc được file, không tìm thấy key word
            return ["N/A"]
        except:
            return ["B"]

    def getDividend(self, 
                     id_company: int = 1301,
                     return_df=False, 
                     save_file=True):
        """
        Parameters
        ----------
        id_company : int
            id of company default is 1301
        return_df : bool
            return dataframe of data default is False
        save_file : bool
            save dataframe of data default is True
        """
        print(id_company, '--------')
        df = pd.read_csv(self.path_save + f"Data/{id_company}/docs/link.csv")
        df_dividend = pd.DataFrame(columns=["Year", "Q1", "Q2", "Q3", "Q4"])
        for quy in ["Q4"]:
            for id in df.index:
                year = df[f"Year"][id]
                df_dividend_year = self.getDividendTableFromPdf(
                    id_company, year, quy
                )
                # print(df_dividend_year)
                df_dividend.loc[(len(df_dividend))] = list(df_dividend_year.iloc[0])
                # df_dividend.loc[(len(df_dividend))] = [year, '1', '1', '1', '1']

        for quy in ["Q1", "Q2", "Q3", "Q4"]:
            list_date = []
            for id in df_dividend.index:
                year = df_dividend["Year"][id]
                if len(re.findall(r"\d+", df_dividend[quy][id])) > 0:
                    date = self.getDataFromPdf(id_company, year, quy)
                    # print(year, quy, date)
                else:
                    date = np.nan
                list_date.append(date)
            df_dividend[f"time_split_{quy}"] = list_date

        if save_file:
            df_dividend.to_csv(
                self.path_save + f"Data/{id_company}/docs/dividend.csv", index=False
            )
        if return_df:
            return df_dividend
