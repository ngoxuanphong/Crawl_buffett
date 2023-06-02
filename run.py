from save_pdf import save_pdf
from get_volume import get_volume
import time
import pandas as pd
import numpy as np

def get_company(id_company = 5486):
    a = time.process_time()

    print('Start', id_company)
    save_pdf(id_company)
    print('Save pdf done')
    get_volume(id_company)
    print('Get volume done')
    b = time.process_time()
    print(int(b-a))

id_company = 3333


# def get_all_com():
#     lst_com = pd.read_csv('List_company_23052023 - Listing.csv')
#     if 'check' not in lst_com.columns:
#         lst_com['check'] = np.nan
#     for i in lst_com.index:
#         id_company = lst_com['Symbol'][i]
#         check = lst_com['Symbol'][i]
#         if check != 'Done':
#             try:
#                 get_company(id_company=id_company)
#                 msg = 'Done'
#             except: 
#                 msg = 'False'
#             lst_com['check'][i] = msg
#             lst_com.to_csv('List_company_23052023 - Listing.csv', index = False)

# get_all_com()
get_company(3333)