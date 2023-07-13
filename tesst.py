# import threading as th
from multiprocessing import Process
from src.savePDF import GetProxyDriver, GetPDF
import time 

thread_num = 7


def run():
    bf = GetPDF(
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        time_sleep=10,
        browser_name='Thread',
        # driver_temp= driver
    )
    # bf.savePDFThread(reverse=True)
    bf.thread_file(reverse=False)

if __name__ == "__main__":  # confirms that the code is under main function
    procs = []
    for id_process in range(thread_num):
        # proc = th.Thread(target=run, args=())
        proc = Process(target=run, args=())
        time.sleep(5)
        proc.start()
        procs.append(proc)
    for proc in procs:
        proc.join()
    print("Done")
