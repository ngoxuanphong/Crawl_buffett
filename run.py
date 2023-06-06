from datetime import datetime
from save_pdf import save_pdf
from get_volume import get_volume
import logging
import time
import pandas as pd
import numpy as np

logging.getLogger("selenium.webdriver.common.selenium_manager").setLevel(logging.WARNING)
def get_company(id_company = 5486):
    a = time.process_time()

    print('Start', id_company)
    save_pdf(id_company)
    print('Save pdf done')
    # get_volume(id_company)
    # print('Get volume done')
    # b = time.process_time()
    # print(int(b-a))


def get_all_com(csv_file = 'docs/List_company_23052023 - Listing.csv'):
    log_path = csv_file.replace('.csv', '.log').replace('docs/', 'logs/')
    logging.basicConfig(filename=log_path, level=logging.INFO)
    lst_com = pd.read_csv(csv_file)
    if 'check' not in lst_com.columns:
        lst_com['check'] = np.nan
    for i in lst_com.index:
        id_company = lst_com['Symbol'][i]
        check = lst_com['check'][i]
        if check != 'Done':
            try:
                get_company(id_company=id_company)
                msg = 'Done'
                log_message(f'Successfully: ID {id_company}')
            except:
                msg = 'False'
                log_message(f'Failed: ID {id_company}')
            lst_com['check'][i] = msg
            lst_com.to_csv(csv_file, index=False)
        

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'{timestamp} - {message}')