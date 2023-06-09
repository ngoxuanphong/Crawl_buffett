import tabula, camelot, os, time
import os, time
import pandas as pd
import numpy as np
import warnings
import requests
import ocrmypdf


def convert_table(df):
    df.loc[-1] = df.columns
    df = df.sort_index()
    df.columns = np.arange(len(df.columns))
    return df.reset_index(drop=True)

def find_row(df, text):
    list_id = np.where((df[0].str.find(text) > 0) == True)[0]
    if len(list_id) == 0:
        return None
    else:
        return list_id[0] 
    
def get_vol_table_tabula(file_path):
    if 'https' in file_path:
        tables = tabula.read_pdf(file_path, pages="all", multiple_tables=True, silent=True, stream=True)
    else:
        tables = tabula.read_pdf(file_path, pages="all", multiple_tables=True, silent=True)
    for table in range(len(tables)):
        df = pd.DataFrame(tables[table])
        df = convert_table(df)
        row_id = find_row(df, "期末発行済株式数(自己株式を含む)")
        if row_id is not None and len(df.columns) < 10 and len(df[0][0]) < 100:
            return df
    return None

def cut_vol_table(tables):
    for i in range(len(tables)):
        df = tables[i].df
        df_find_key = df[0].str.find('期末発行済株式数（自己株式を含む）')
        for i in df_find_key.index:
            if df_find_key[i] >= 0:
                id_have_key = i
                df = df.iloc[id_have_key:, :].reset_index(drop=True)
                return df

def convert_table_mix_data(df):
    df_add = df[3].str.split(' ', expand=True)
    df_add2 = df[4].str.split(' ', expand=True)
    for i in df.index:
        if df[2][i] == '':
            df[2][i] = df_add[0][i]
            df[3][i] = df_add[1][i]
        if df[5][i] == '':
            df[5][i] = df_add2[1][i]
            df[4][i] = df_add2[0][i]
    return df
     
def drop_empty_col(df):
    for col in df.columns:
        if (df[col]=='').all():
            df = df.drop(columns=col)
    df.columns = np.arange(len(df.columns))
    return df

def get_vol_table_camelot(file_path):
    tables = camelot.read_pdf(file_path, pages="all", multiple_tables=True, flavor="stream", suppress_stdout=True)
    df = cut_vol_table(tables)
    # print(df)
    df = convert_table_mix_data(df)
    df = drop_empty_col(df)
    return df

def get_vol_table(file_path = 'tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf'):
    df = get_vol_table_tabula(file_path)
    if df is None:
        df = get_vol_table_camelot(file_path)
    return [int(df[2][0].replace(' 株', '').replace(',', '')), int(df[2][1].replace(' 株', '').replace(',', ''))]


def ocr_pdf(input_file, output_file = 'tests/ocr.pdf'):
    ocrmypdf.ocr(input_file, output_file,
                    language= 'eng+jpn',
                    force_ocr = True,
                    output_type='pdf',
                    optimize=0,
                    progress_bar = False,
                    # skip_big = True,
                    max_image_mpixels = 500,
                    )