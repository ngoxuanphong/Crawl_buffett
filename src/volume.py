import pdfplumber
import pandas as pd
import numpy as np
import os, re
from src.ocrPdf import ocrPDF

class GetVolume():
    def __init__(self, 
                 path_save="tests/"):
        """
        Parameters
        ----------
        path_save : str
            Path to save data default is "tests/"
        """
        self.path_save = path_save

    def openPdf(self, 
                path: str = "tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf"):
        """
        Parameters
        ----------
        path : str
            Path to pdf file default is "tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf"
        """
        pdf = pdfplumber.open(path)
        return pdf

    def findText(self,
                    pdf: pdfplumber.pdf.PDF,
                    text: str = "期末発行済株式数"):
        """
        Parameters
        ----------
        pdf : pdfplumber.pdf.PDF
            pdf file
        text : str
            text to find default is "期末発行済株式数"
        """
        for page in range(len(pdf.pages)):
            text = pdf.pages[page].extract_text()
            text = text.replace('\n', ' ').replace('|', '').replace(' ', '').replace('.', ',').replace('ー', '123,456,789,999').replace('－', '123,456,789,999').replace('―', '123,456,789,999').replace('-', '123,456,789,999').replace('−', '123,456,789,999').replace('—', '123,456,789,999')
            text_first = '期末発行済株式数'
            id_first = text.find(text_first)
            if id_first >= 0:
                text = text[id_first:]
                return text

    def findData(self,
                 path: str = "tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf",
                 year = 2022):
        """
        Parameters
        ----------
        path : str
            Path to pdf file default is "tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf"
        """
        pdf = self.openPdf(path)
        text = self.findText(pdf)
        numbers = re.findall(r"[QＱ](\d{1,3}(?:,\d{3})*)", text)
        print(text)
        if len(numbers) == 0:
            print('1---', numbers)
            numbers = re.findall(r"[期](\d{1,3}(?:,\d{3})*)", text)
            numbers = [int(number.replace(",", "")) for number in numbers]
            numbers = [0 if number == 123456789999 else number for number in numbers ]
            return [numbers[0], numbers[2]]
        else:
            print('2---', numbers)
            numbers = [int(number.replace(",", "")) for number in numbers]
            numbers = [0 if number == 123456789999 else number for number in numbers ]
            return [numbers[0], numbers[1]]
    
    def getDataFromPdf(self,
                        id_company: int = 1301,
                        year: int = 2022,
                        quy: str = "Q1",):
        """
        Parameters
        ----------
        id_company : int
            id of company default is 1301
        year : int
            year of data default is 2022
        quy : str
            quy of data default is "Q1"
        """

        for file in os.listdir(self.path_save + f"Data/{id_company}/PDF"):
            if file.startswith(f"{year}_{quy}") and ("(訂正)" not in file) and '_ocr' not in file:
                file_name = file
                input_path = self.path_save + f"Data/{id_company}/PDF/{file_name}"
                date_volume = file_name[file_name.find("(") + 1 : file_name.find(")")]
                try:
                    lst_data_of_time = self.findData(input_path, year)
                except:
                    try:
                        path_pdf_ocr = input_path.replace(".pdf", "_ocr.pdf")
                        print('Need ocr', path_pdf_ocr)
                        if not os.path.exists(path_pdf_ocr):
                            ocrPDF(input_path)
                        lst_data_of_time = self.findData(path_pdf_ocr, year)
                    except Exception as e:
                        print(f"{id_company}_{year}_{quy}: {e}")
                        lst_data_of_time = ["N/A", "N/A"]
                print(f"{id_company}_{year}_{quy}: {lst_data_of_time}")
                return [date_volume] + lst_data_of_time
        return ["N/A", "N/A", "N/A"]
    

    def getVolume(self,
                  id_company: int = 1301,
                  return_df: bool = False,
                  save_file: bool = True,):
        """
        Parameters
        ----------
        id_company : int
            id of company default is 1301
        return_df : bool
            return DataFrame of data default is False
        save_file : bool
            save DataFrame of data default is True
        """
        df_volume = pd.DataFrame(columns=["time", "date", "vol1", "vol2"])
        df = pd.read_csv(self.path_save + f"Data/{id_company}/docs/link.csv")
        for quy in ["Q1", "Q2", "Q3", "Q4"]:
            for id in df.index:
                if 'year' in df.columns:
                    year = df[f"Year"][id]
                else:
                    year = df.iloc[id, 0][2:6]
                df_volume.loc[(len(df_volume))] = [f"{year}_{quy}"] + self.getDataFromPdf(
                    id_company, year, quy)
        if save_file:
            df_volume.to_csv(self.path_save + f"Data/{id_company}/docs/volume.csv", index=False)
        if return_df:
            return df_volume
