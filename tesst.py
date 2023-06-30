import threading as th
from src.savePDF import GetProxyDriver, GetPDF
import time 

thread_num = 5


def run(driver):
    bf = GetPDF(
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="tests/Data",
        time_sleep=35,
        browser_name='Thread',
        driver_temp= driver
    )
    bf.savePDFThread()

if __name__ == "__main__":  # confirms that the code is under main function
    get_proxy_driver = GetProxyDriver(thread_num=thread_num)
    lst_driver = get_proxy_driver.getListDriver()
    procs = []
    for id_process in range(thread_num):
        # proc = Process(target=run, args=(names[id_process], lst_driver[id_process],))
        proc = th.Thread(target=run, args=(lst_driver[id_process],))
        time.sleep(3)
        proc.start()
        procs.append(proc)
    for proc in procs:
        proc.join()
    print("Done")
