from selenium import webdriver
import time

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the first tab
driver.get("https://www.google.com")

# Open additional tabs
driver.execute_script("window.open('https://www.facebook.com')")

# Switch to the first tab
driver.switch_to.window(driver.window_handles[0])
time.sleep(2)
driver.execute_script("window.open('https://www.twitter.com')")
driver.execute_script("window.open('https://www.instagram.com')")

# Wait for a few seconds (optional)
time.sleep(2)

# Close the first tab
driver.close()

# Switch to the next tab
driver.switch_to.window(driver.window_handles[0])
time.sleep(2)
# Close the second tab
driver.close()

# Switch to the last tab
driver.switch_to.window(driver.window_handles[0])
time.sleep(2)
# Close the third tab
driver.close()
time.sleep(2)
# Close the WebDriver
driver.quit()
