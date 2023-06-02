from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import pandas as pd
from time import sleep

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('enable-automation')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('--disable-gpu')

br = webdriver.Chrome(chrome_options=chrome_options)

br.get('https://www.google.com.vn/?hl=vi')
br.get('https://github.com/ngoxuanphong/Crawl_buffett')
print(br.title)