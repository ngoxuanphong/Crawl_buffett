# import threading as th
from multiprocessing import Process
from src.savePDF import GetPpfIrbank
from src.savePDF import GetPDF
import time 

thread_num = 20


def run():
    bf = GetPDF(
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        time_sleep=10,
        browser_name='Thread',
        # driver_temp= driver
    )
    # bf.savePDFThread(reverse=True)
    bf.multiThreadMakeCheckFile()
    bf.multiThreadFile(reverse=False)

if __name__ == "__main__":  # confirms that the code is under main function
    # procs = []
    # for id_process in range(thread_num):
    #     # proc = th.Thread(target=run, args=())
    #     proc = Process(target=run, args=())
    #     time.sleep(5)
    #     proc.start()
    #     procs.append(proc)
    # for proc in procs:
    #     proc.join()

    irbank = GetPpfIrbank(path_all_com="docs/List_company_23052023 - Listing.csv",
                          path_save="Data",)
    # irbank.getAllCom()
    for symbol in [9399,
 9651,
 9797,
 8184,
 2538,
 7968,
 3318,
 4842,
 6669,
 7853,
 7432,
 5398,
 3785,
 4850,
 5012,
 3394,
 2132,
 8248,
 2128,
 4989,
 6661,
 4358,
 4589,
 2369,
 2399,
 6593,
 4798,
 1405,
 5412,
 2006,
 3331,
 7714,
 3811,
 6784,
 3859,
 6052,
 7861,
 3827,
 3715,
 3225,
 9648,
 2182]:
        try:
            irbank.savePDF(symbol=symbol)
        except:
            pass
