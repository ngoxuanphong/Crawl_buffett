import PyPDF2
import re
import os
import time
import pandas as pd
import numpy as np
import warnings
from volume.ocr_volume import ocr_pdf

warnings.simplefilter("ignore", UserWarning)


def convert_pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            t = page.extract_text()
            text += t
    
    return text

def get_time_dividend(time_text):
    matches = re.findall(r'\d+', time_text)
    if (time_text[0: 2] =='平成' or time_text[0: 2] == '20') and len(matches) == 3 :
        if int(matches[0]) > 2000:
            return [f'{int(matches[2])}_{int(matches[1])}_{int(matches[0])}']
        else:
            return [f'{int(matches[2])}_{int(matches[1])}_{int(matches[0]) + 1988 }']
    return 0
    
def get_data_from_pdf(id_company, year, quy, path_save = ''):
    # print(f'{year}_{quy}')
    try:
        for file in os.listdir(path_save + f'Data/{id_company}/PDF'):
            if file.startswith(f'{year}_{quy}') and '(訂正)' not in file:
                file_name = file
                path_of_file = path_save + f'Data/{id_company}/PDF/{file_name}'
                text = convert_pdf_to_text(path_of_file)
                text = text.replace(" ", "")
                idx = text.find('配当支払開始予定日')
                if idx != -1:
                    time_text = text[idx + 9: idx + 20]
                    temp = get_time_dividend(time_text)
                    if temp:
                        # print(0)
                        return temp
                else:
                    ocr_file = path_of_file.replace('.pdf', '_ocr.pdf')
                    if os.path.exists(ocr_file) == False:
                        ocr_pdf(path_of_file)
                    text_ = convert_pdf_to_text(ocr_file)
                    text_ = text_.replace(" ", "")

                    idx = text_.find('配当支払開始予定日')
                    if idx != -1:
                        _ = text_.find('四半期報告書提出予定日')
                        if text_[ _+ 11: _+14] == '\n配当' :
                            return ['B']
                        
                        time_text = text_[idx + 9: idx + 20]
                        temp = get_time_dividend(time_text)
                        if temp:
                            # print(1)
                            return temp
                        
                    #case 1:
                    idx = text_.find('配当文払開始予定日')
                    if idx != -1:
                        time_text = text_[idx + 9: idx + 20]
                        temp = get_time_dividend(time_text)
                        if temp:
                            # print(2)
                            return temp
                        
                    # Case 2: 
                    if text_.find('配当') != -1 :
                        idx = text_.find('TEL')
                        time_text = text_[idx + 16: idx + 27]
                        temp = get_time_dividend(time_text)
                        if temp:
                            # print(3)
                            return temp
                        
                return ['']
        return ['N/A']
    except:
        return ['B']


def get_dividend(id_company, 
               path_save = '', 
               return_df = False, 
               save_file = True):
    df_volume = pd.DataFrame(columns=['time', 'time2'])
    df = pd.read_csv(path_save + f'Data/{id_company}/docs/link.csv')
    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        for id in df.index:
            year = df[f'Year'][id]
            data = get_data_from_pdf(id_company, year, quy, path_save)
            # print(data)
            df_volume.loc[(len(df_volume))] = [f'{year}_{quy}'] + data
    if save_file:
        df_volume.to_csv(path_save + f'Data/{id_company}/docs/dividend.csv', index=False)
    if return_df:
        return df_volume
