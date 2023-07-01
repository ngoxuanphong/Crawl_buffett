import threading as th
from src.savePDF import GetProxyDriver, GetPDF
import time 

thread_num = 6


def run():
    bf = GetPDF(
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        time_sleep=20,
        browser_name='Thread',
        # driver_temp= driver
    )
    bf.savePDFThread()

if __name__ == "__main__":  # confirms that the code is under main function
    # get_proxy_driver = GetProxyDriver(thread_num=thread_num)
    # lst_driver = get_proxy_driver.getListDriver()
    procs = []
    for id_process in range(thread_num):
        proc = th.Thread(target=run, args=())
        time.sleep(3)
        proc.start()
        procs.append(proc)
    for proc in procs:
        proc.join()
    print("Done")
