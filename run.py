from getlink import FinancailStatement, create_link_df
from read_pdf import get_vol_table
import pandas as pd
import os

def save_csv(F, df, id_company, df_check):
    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        for year in df.index:
            for id_link in range(len(df[f'Time_{quy}'][year])):
                link_preview = df[f'Link_{quy}'][year][id_link]
                link_pdf = F.get_pdf_link(link_preview)
                name = df[f'Time_{quy}'][year][id_link]
                if link_preview != 'https://www.buffett-code.com#':
                    print(year, quy, link_pdf)
                    try:
                        df_vol = get_vol_table(link_pdf)
                        df_vol.to_csv(f'{id_company}/{year}_{quy}.csv', index=False)
                        df_check[f'Link_{quy}'][year][id_link] = 'Done'
                    except:
                        df_check[f'Link_{quy}'][year][id_link] = 'Error'
                    df_check.to_csv(f'{id_company}/docs/checklist.csv')


def get_vol_buffett(id_company):
    if not os.path.exists(f'{id_company}'):
        os.mkdir(f'{id_company}')
    if not os.path.exists(f'{id_company}/docs'):
        os.mkdir(f'{id_company}/docs')

    F = FinancailStatement()
    table = F.get_table(id_company = id_company)
    df = create_link_df(table)

    df_check = df.copy()
    df.to_csv(f'{id_company}/link.csv')
    df_check.to_csv(f'{id_company}/docs/checklist.csv')

    save_csv(F, df, id_company, df_check)


get_vol_buffett(5468)