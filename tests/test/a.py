import selenium, time
import random
import string
from PIL import Image
import easyocr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import edge

from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

def crop_image(MAY):
    im = Image.open(f'screenshot{MAY}.png')
    im = im.crop((1000, 525, 1050, 555))
    im.save(f'CROP_{MAY}.png')
    # im.show()

def get_ocr(MAY):
    crop_image(MAY)
    # Tạo một đối tượng OCR
    reader = easyocr.Reader(['en'])  # 'en' là mã ngôn ngữ tiếng Anh

    # Đường dẫn đến tệp ảnh bạn muốn OCR
    image_path = f'CROP_{MAY}.png'

    # Thực hiện OCR trên ảnh
    results = reader.readtext(image_path)
    return results[0][1].upper().replace(' ', '')

def get_user():
    name = [
        "An",
        "Binh",
        "Cao",
        "Dung",
        "Hanh",
        "Hoa",
        "Hien",
        "Hoang",
        "Hung",
        "Lam",
        "Linh",
        "Minh",
        "Nam",
        "Nga",
        "Ngoc",
        "Phong",
        "Quang",
        "Quyen",
        "Sang",
        "Thao"
    ]

    last_names = [
    "Nguyen",
    "Tran",
    "Le",
    "Pham",
    "Huynh",
    "Hoang",
    "Phan",
    "Vu",
    "Dang",
    "Bui",
    "Do",
    "Ho",
    "Ngo",
    "Duong",
    "Ly",
    "Dao",
    "Doan",
    "Bach",
    "Luong",
    "Phung"
]
    name = name + last_names + random.randint(1000, 9999)
    
    return name

def login(driver, MAY):
    print('Đang đăng nhập', end=' ')
    driver.get("https://au.vtc.vn/auonstage")
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div[2]/a').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="cg_tab2_login"]/a[2]').click()
    time.sleep(0.5)
    random_chars = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    driver.find_element(By.ID, 'txtUserNameDK').send_keys(random_chars)
    driver.find_element(By.ID, 'txtPassDK').send_keys(123456)
    driver.find_element(By.ID, 'txtPassDK2').send_keys(123456)

    # take screenshot
    driver.save_screenshot(f'screenshot{MAY}.png')
    capcha = get_ocr(MAY)
    print(capcha, end=' ')
    
    driver.find_element(By.ID, 'txCaptchaInput').send_keys(capcha)
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="cg_tab2_login"]/div[1]/a').click()
    time.sleep(1)

def logout(driver):
    driver.get("https://au.vtc.vn/auonstage")
    time.sleep(0.5)
    for i in range(3):
        try:
            time.sleep(0.5)
            driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div[2]/a[2]').click()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print('Đã Logout')
            break
        except Exception as e:
            pass

def vote(driver):
    time.sleep(0.5)
    for i in range(3):
        try:
            driver.find_element(By.XPATH, '//*[@id="app-vote"]/div[9]/p/img').click()
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            if 'Đại học Ngoại thương' in soup.text:
                print('Đã vote', end=' ')
                driver.find_element(By.XPATH, '//*[@id="app-vote"]/div[2]/div/span[2]/p').click()
                time.sleep(1)
                break
        except Exception as e:
            # print(e)
            pass

def run(MAY):
    j = 0
    while True:
        options = edge.options.Options()
        options.add_argument("--headless=new")
        driver = webdriver.Edge(options=options)
        driver.set_window_size(1920, 1080)
        for i in range(10):
            print('Lần', 10*j + i, 'Máy:', MAY, end=' ')
            try:
                login(driver, MAY)
                vote(driver)
                logout(driver)
            except:
                print('Lỗi')
                pass
        j += 1
        print('Đã vote', 10*(j+1), 'lần')

        driver.close()

run(1)
# from multiprocessing import Process
# thread_num = 5

# if __name__ == "__main__":  # confirms that the code is under main function
#     procs = []
#     for id_process in range(thread_num):
#         # proc = th.Thread(target=run, args=())
#         proc = Process(target=run, args=(id_process,))
#         time.sleep(5)
#         proc.start()
#         procs.append(proc)
#     for proc in procs:
#         proc.join()
