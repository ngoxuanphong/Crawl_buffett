import tabula, os, re
import os
import pandas as pd
import numpy as np
import warnings
from src.ocrpdf import ocr_pdf, convert_pdf_to_text
import PyPDF2
import warnings

warnings.simplefilter("ignore", UserWarning)


class GetDividend:
    def __init__():
        pass

    def get_dividend_table(self, tables, year="Any", table_id=4):
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

    def get_dividend_table_from_pdf(self, id_company, year, quy="Q4", path_save=""):
        for file in os.listdir(path_save + f"Data/{id_company}/PDF"):
            if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
                file_name = file
                path_of_file = path_save + f"Data/{id_company}/PDF/{file_name}"
                try:
                    tables = tabula.read_pdf(
                        path_of_file, pages="all", multiple_tables=True, silent=True
                    )
                    df = self.get_dividend_table(tables, year)
                    if len(df.index) == 1:
                        return df
                except:
                    try:
                        ocr_file = path_of_file.replace(".pdf", "_ocr.pdf")
                        if os.path.exists(ocr_file) == False:
                            ocr_pdf(path_of_file)
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

    def get_time_dividend(self, time_text):
        matches = re.findall(r"\d+", time_text)
        if (time_text[0:2] == "平成" or time_text[0:2] == "20") and len(matches) == 3:
            if int(matches[0]) > 2000:
                return [f"{int(matches[2])}_{int(matches[1])}_{int(matches[0])}"]
            else:
                return [
                    f"{int(matches[2])}_{int(matches[1])}_{int(matches[0]) + 1988 }"
                ]
        return 0

    def get_data_from_pdf(self, id_company, year, quy, path_save=""):
        # print(f'{year}_{quy}')
        try:
            for file in os.listdir(path_save + f"Data/{id_company}/PDF"):
                if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
                    file_name = file
                    path_of_file = path_save + f"Data/{id_company}/PDF/{file_name}"
                    text = convert_pdf_to_text(path_of_file)
                    text = text.replace(" ", "")
                    idx = text.find("配当支払開始予定日")
                    if idx != -1:
                        time_text = text[idx + 9 : idx + 20]
                        temp = self.get_time_dividend(time_text)
                        if temp:
                            # print(0)
                            return temp
                    else:
                        ocr_file = path_of_file.replace(".pdf", "_ocr.pdf")
                        if os.path.exists(ocr_file) == False:
                            ocr_pdf(path_of_file)
                        text_ = convert_pdf_to_text(ocr_file)
                        text_ = text_.replace(" ", "")

                        idx = text_.find("配当支払開始予定日")
                        if idx != -1:
                            _ = text_.find("四半期報告書提出予定日")
                            if text_[_ + 11 : _ + 14] == "\n配当":
                                return ["B"]

                            time_text = text_[idx + 9 : idx + 20]
                            temp = self.get_time_dividend(time_text)
                            if temp:
                                # print(1)
                                return temp

                        # case 1:
                        idx = text_.find("配当文払開始予定日")
                        if idx != -1:
                            time_text = text_[idx + 9 : idx + 20]
                            temp = self.get_time_dividend(time_text)
                            if temp:
                                # print(2)
                                return temp

                        # Case 2:
                        if text_.find("配当") != -1:
                            idx = text_.find("TEL")
                            time_text = text_[idx + 16 : idx + 27]
                            temp = self.get_time_dividend(time_text)
                            if temp:
                                # print(3)
                                return temp

                    return [""]
            return ["N/A"]
        except:
            return ["B"]

    def get_dividend(self, id_company, path_save="", return_df=False, save_file=True):
        df = pd.read_csv(path_save + f"Data/{id_company}/docs/link.csv")
        df_dividend = pd.DataFrame(columns=["Year", "Q1", "Q2", "Q3", "Q4"])
        for quy in ["Q4"]:
            for id in df.index:
                year = df[f"Year"][id]
                df_dividend_year = self.get_dividend_table_from_pdf(
                    id_company, year, quy, path_save
                )
                print(df_dividend_year)
                df_dividend.loc[(len(df_dividend))] = list(df_dividend_year.iloc[0])
        for quy in ["Q1", "Q2", "Q3", "Q4"]:
            list_date = []
            for id in df_dividend.index:
                year = df_dividend["Year"][id]
                if len(re.findall(r"\d+", df_dividend[quy][id])) > 0:
                    date = self.get_data_from_pdf(id_company, year, quy, path_save)
                    print(year, quy, date)
                else:
                    date = np.nan
                list_date.append(date)
            df_dividend[f"time_split_{quy}"] = list_date
        if save_file:
            df_dividend.to_csv(
                path_save + f"Data/{id_company}/docs/dividend.csv", index=False
            )
        if return_df:
            return df_dividend
