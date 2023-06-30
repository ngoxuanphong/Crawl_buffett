import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.proxynova.com/proxy-server-list/'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')
tables = soup.find_all('table', id='tbl_proxy_list')

df = pd.read_html(str(tables[0]))[0]
print(df)
print(len(tables))