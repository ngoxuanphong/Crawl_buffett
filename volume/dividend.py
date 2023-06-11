import tabula, camelot, os, time
import os, time
import pandas as pd
import numpy as np
import warnings
import requests
from ocr_volume import ocr_pdf

def get_dividend_table(tables, 
                       year = 'Any', 
                       table_id = 4):
    df = pd.DataFrame(tables[table_id])
    df.dropna(subset=df.columns[0], inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df.columns = np.arange(len(df.columns))
    df.drop(columns=df.columns[5:], inplace=True)
    df.dropna(axis=0, how='all', inplace=True)
    df = df.reset_index(drop=True)
    df = df.iloc[[1]]
    df.columns = [year, 'Q1', 'Q2', 'Q3', 'Q4']
    df[year].iloc[0] = year
    if (pd.isna(df.iloc[0]) == False).all() and (df.iloc[0, 1:].str.len() < 10).all():
        return df.reset_index(drop=True)
    raise Exception('Khong tim thay bang co du lieu')

def get_dividend_table_from_pdf(id_company, year, 
                                quy = 'Q4', 
                                path_save = ''):
    for file in os.listdir(path_save + f'Data/{id_company}/PDF'):
        if file.startswith(f'{year}_{quy}') and '(訂正)' not in file:
            file_name = file
            # print(file_name)
            path_of_file = path_save + f'Data/{id_company}/PDF/{file_name}'
            try:
                tables = tabula.read_pdf(path_of_file, pages="all", multiple_tables=True, silent=True)
                df = get_dividend_table(tables, year)
                if len(df.index) == 1: return df
            except:
                try:
                    ocr_file = path_of_file.replace('.pdf', '_ocr.pdf')
                    if os.path.exists(ocr_file) == False:
                        ocr_pdf(path_of_file)
                    tables = tabula.read_pdf(ocr_file, pages="all", multiple_tables=True, silent=True)
                    df = get_dividend_table(tables, year)
                    if len(df.index) == 1: return df
                except:
                    print('Nawm nay dang bi loi', year)
                    try:
                        df = get_dividend_table(tables, year, table_id = 3)
                        if len(df.index) == 1: return df
                    except:
                        pass
            return pd.DataFrame({year: year, 'Q1':'B', 'Q2':'B', 'Q3':'B', 'Q4':'B'}, index=[0])
        
    return pd.DataFrame({year: year, 'Q1':'N/A', 'Q2':'N/A', 'Q3':'N/A', 'Q4':'N/A'}, index=[0])

def get_dividend(id_company, 
               path_save = '', 
               return_df = False, 
               save_file = True):
    df = pd.read_csv(path_save + f'Data/{id_company}/docs/link.csv')
    df_dividend = pd.DataFrame(columns=['Year', 'Q1', 'Q2', 'Q3', 'Q4'])
    for quy in ['Q4']:
        for id in df.index:
            year = df[f'Year'][id]
            df_dividend_year = get_dividend_table_from_pdf(id_company, year, quy, path_save)
            print(df_dividend_year)
            df_dividend.loc[(len(df_dividend))] = list(df_dividend_year.iloc[0])
    return df_dividend

df_dividend = get_dividend(1301, path_save='tests/')
df_dividend.to_csv('tests/Data/1301/docs/dividend.csv', index=False)