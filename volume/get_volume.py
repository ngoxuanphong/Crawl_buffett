import PyPDF2
import re
import os
import time
import pandas as pd
import numpy as np
import warnings
from volume.ocr_volume import get_vol_table, ocr_pdf
warnings.simplefilter("ignore", UserWarning)


def convert_pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
    
    return text


def find_by_re(text2):
    # print(text2)
    text2 = text2.replace(' ', '')  
    numbers = re.findall(r'\d{1,3}(?:,\d{3})*', text2)
    # print(numbers)
    filtered_numbers = [int(number.replace(',', '')) for number in numbers if int(number.replace(',', '')) > 3000]
    if len(filtered_numbers) >= 3:
        lst_data_of_time = [filtered_numbers[0], filtered_numbers[2]]
    elif len(filtered_numbers) == 2:
        lst_data_of_time = filtered_numbers
    else:
        lst_data_of_time = [np.nan,np.nan]
    return lst_data_of_time

def convert_text(text1):
    matches = re.finditer('株', text1)
    positions = [match.start() for match in matches]

    text2 = text1[:positions[-1]+1]
    text2 = text2.replace('③', '\n③').replace(' ,', ',')
    return find_by_re(text2)

def find_row(text):
    text1 = text[text.find('期末発行済株式数') :text.find('期末発行済株式数')+125]
    text3 = convert_text(text1)
    if text3 == [np.nan,np.nan] and text1 != '':
        text1 = text[text.find('期末発行済株式数') :text.find('期末発行済株式数')+300]
        text3 = convert_text(text1)
    return text3

def get_data_from_pdf(id_company, year, quy, 
                      path_save = ''):
    for file in os.listdir(path_save + f'Data/{id_company}/PDF'):
        if file.startswith(f'{year}_{quy}') and '(訂正)' not in file:
            file_name = file
            text = convert_pdf_to_text(path_save + f'Data/{id_company}/PDF/{file_name}')
            date_volume = file_name[file_name.find('(')+1:file_name.find(')')]
            try:
                lst_data_of_time = find_row(text)
            except:
                try:
                    lst_data_of_time = get_vol_table(path_save + f'Data/{id_company}/PDF/{file_name}')
                except:
                    try:
                        ocr_pdf(path_save + f'Data/{id_company}/PDF/{file_name}')
                        text = convert_pdf_to_text('tests/ocr.pdf')
                        lst_data_of_time = find_row(text.replace(' ', '').replace('.', ','))
                    except:
                        lst_data_of_time = ['B',"B"]
            print(f'{year}_{quy}: {lst_data_of_time}')
            return [date_volume] + lst_data_of_time
    return ['N/A', 'N/A','N/A']


def get_volume(id_company, 
               path_save = '', 
               return_df = False, 
               save_file = True):
    df_volume = pd.DataFrame(columns=['time', 'time2', 'vol1', 'vol2'])
    df = pd.read_csv(path_save + f'Data/{id_company}/docs/link.csv')
    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        for id in df.index:
            year = df[f'Year'][id]
            df_volume.loc[(len(df_volume))] = [f'{year}_{quy}'] + get_data_from_pdf(id_company, year, quy, path_save)
    if save_file:
        df_volume.to_csv(path_save + f'Data/{id_company}/docs/volume.csv', index=False)
    if return_df:
        return df_volume
