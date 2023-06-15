from datetime import datetime
import time,requests
import pandas as pd
import numpy as np
from save_pdf import FinancialStatement

def back_test_all_com(csv_file = 'docs/List_company_23052023 - Listing.csv'):
    lst_com = pd.read_csv(csv_file)
    print(lst_com)

    for i in lst_com.index:
        id_company = lst_com['Symbol'][i]
        check = lst_com['check'][i]
        if check == 'Done':
            back_test_comany(id_company)

def back_test_comany(id_company = 1376):
    F = FinancialStatement()
    df_check = pd.read_csv(f'Data/{id_company}/docs/check.csv')
    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        df_check[f'Link_{quy}'] = df_check[f'Link_{quy}'].str.replace("']", '').str.replace("['", '').str.split("', '")
        df_check[f'Time_{quy}'] = df_check[f'Time_{quy}'].str.replace("']", '').str.replace("['", '').str.split("', '")
        for id in df_check.index:
            if df_check[f'download_{quy}'][id] != 'OK' and df_check[f'Link_{quy}'][id] != []:
                year = df_check[f'Year'][id]
                print(id_company, year, quy, df_check[f'Link_{quy}'][id])
                for id_link in range(len(df_check[f'Time_{quy}'][id])):
                    year_ = df_check[f'Year'][id]
                    link_preview = df_check[f'Link_{quy}'][id][id_link]
                    if not 'https://www.buffett-code.com/company' in link_preview:
                        msg = 'Nan'
                    else:
                        try:
                            check_done_quater = False
                            link_pdf = F.get_pdf_link(link_preview)
                            name = df_check[f'Time_{quy}'][id][id_link].replace(' ', '').replace('/', '_')
                            response = requests.get(link_pdf)
                            with open(f'Data/{id_company}/PDF/{year_}_{quy}_{name}.pdf', 'wb') as f:
                                f.write(response.content)
                            msg = 'OK'
                        except:
                            msg = None
                    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'Data/{id_company} - {year_} - {quy} - {id_link} - {link_preview} - {time_now}')
                    df_check[f'download_{quy}'][id] = msg
                    df_check.to_csv(f'Data/{id_company}/docs/check.csv', index=False)
                    time.sleep(np.random.randint(25,30))
