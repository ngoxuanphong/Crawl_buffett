import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


tor_proxy = "127.0.0.1:9150"

chrome_options = Options()

'''chrome_options.add_argument("--test-type")'''
chrome_options.add_argument('--ignore-certificate-errors')
'''chrome_options.add_argument('--disable-extensions')'''
chrome_options.add_argument('disable-infobars')
'''chrome_options.add_argument("--incognito")'''
chrome_options.add_argument('--user-data=C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data\\Default')
chrome_options.add_argument('--proxy-server=socks5://%s' % tor_proxy)
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.buffett-code.com/')
time.sleep(4)