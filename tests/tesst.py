from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
import os
import subprocess

profile_path = os.path.expandvars(
    r"A:\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default"
)

options = Options()
options.set_preference("profile", profile_path)
service = Service(executable_path=GeckoDriverManager().install())
options.binary_location = r"A:\Tor Browser\Browser\firefox.exe"
options.set_preference("network.proxy.type", 1)
options.set_preference("network.proxy.socks", "127.0.0.1")
options.set_preference("network.proxy.socks_port", 9050)

# tor_exe = subprocess.Popen(r"A:\Tor Browser\Browser\firefox.exe")
driver = Firefox(service=service, options=options)
driver.implicitly_wait(5)

time.sleep(3)
element = driver.find_element("id", "connectButton").click()
time.sleep(3)
driver.get("https://check.torproject.org")
driver.get("https://www.buffett-code.com/")
time.sleep(3)


# import os, time
# import subprocess

# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager

# def first_tor():
#     profile_path = os.path.expandvars(
#         r"A:\Tor Browser\Browser\TorBrowser\Data\Browser\profile.default"
#     )
#     options = Options()
#     options.set_preference("profile", profile_path)
#     service = Service(
#         # os.path.expandvars(r"%USERPROFILE%\Desktop\Tor Browser\Browser\firefox.exe"),
#         executable_path=GeckoDriverManager().install()
#     )

#     options.set_preference("network.proxy.type", 1)
#     options.set_preference("network.proxy.socks", "127.0.0.1")
#     options.set_preference("network.proxy.socks_port", 9050)
#     options.set_preference("network.proxy.socks_remote_dns", False)


#     def main():
#         def cleanup(tor_exe):
#             driver.quit()
#             print(tor_exe.pid)
#             tor_exe.kill()

#         tor_exe = subprocess.Popen(
#             os.path.expandvars(
#                 r"A:\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
#             )
#         )
#         driver = Firefox(service=service, options=options)
#         driver.get("https://check.torproject.org")
#         time.sleep(1)
#     main()

# first_tor()
