from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time
import os

browser = None
def get_browser():
    global browser  
    # only one instance of a browser opens, remove global for multiple instances
    if not browser: 
        option = webdriver.FirefoxOptions()
        option.binary_location = r'/Applications/Tor Browser.app/Contents/MacOS/firefox'
        browser = webdriver.Firefox(options=option)
    return browser

driver = get_browser()

time.sleep(3)
element = driver.find_element('id', 'connectButton').click()
time.sleep(10)
driver.get("https://www.buffett-code.com/")
time.sleep(3)
driver.quit()