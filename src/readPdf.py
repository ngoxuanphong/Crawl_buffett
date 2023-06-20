import pandas as pd
import numpy as np
import time, os
from src.get_volume import get_volume
from src.get_table import get_table
from src.dividend import GetDividend
class ReadPdf():
    def __init__(
        self,
<<<<<<< HEAD
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="",
=======
        path_all_com="Crawl/buffett/docs/List_company_23052023 - Listing.csv",
        path_save="Data",
>>>>>>> 347c62602e734128b529e38c77f4dc61fc72bcec
        ):
        self.path_all_com = path_all_com
        self.path_save = path_save

<<<<<<< HEAD
    def get_all_com(self, 
                    reverse: bool = False,
                    get_volume: bool = False,
                    get_dividend: bool = False,):
=======
    def get_all_com(self, reverse: bool = False):
>>>>>>> 347c62602e734128b529e38c77f4dc61fc72bcec
        """
        Get all company in japan stock
        Parameters
        ----------
        reverse : bool
            reverse list company
        Returns
        -------
        None
        """
        lst_com = pd.read_csv(self.path_all_com)
        if "check" not in lst_com.columns:
            lst_com["check"] = np.nan
        if reverse:
            lst_com = lst_com[::-1]
        for i in lst_com.index:
            id_company = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if check == "Done":
<<<<<<< HEAD
                if get_volume:
                    get_volume(id_company, self.path_save, save_file=True)
                if get_dividend:
                    dividendClass = GetDividend(path_save=self.path_save)
                    dividendClass.get_dividend(id_company, save_file=True)
                
=======
                get_volume(id_company, self.path_save, save_file=True)
                get_table(id_company, self.path_save, save_file=True)
                dividendClass = GetDividend(path_save=self.path_save)
                dividendClass.get_dividend(id_company, save_file=True)
                
            
>>>>>>> 347c62602e734128b529e38c77f4dc61fc72bcec
