from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver = webdriver.Firefox()
driver.get("http://www.python.org")
assert "Python" in driver.title
elem = driver.find_element(By.NAME, "q")
elem.clear()
time.sleep(3)
elem.send_keys("pycon")
time.sleep(3)
elem.send_keys(Keys.RETURN)
time.sleep(3)
assert "No results found." not in driver.page_source
time.sleep(3)
driver.close()