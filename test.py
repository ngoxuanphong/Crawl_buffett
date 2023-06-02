from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import pandas as pd
from time import sleep

br = webdriver.Chrome()
br.get('https://www.google.com.vn/?hl=vi')