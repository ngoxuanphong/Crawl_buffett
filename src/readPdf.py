import pandas as pd
import numpy as np
import time, os
from volume import get_volume
from src.get_table import get_table
from src.dividend import GetDividend
class ReadPdf():
    def __init__(
        self,
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        ):
        self.path_all_com = path_all_com
        self.path_save = path_save

    def get_all_com(self, 
                    reverse: bool = False,
                    bool_get_volume: bool = True,
                    bool_get_dividend: bool = True,
                    bool_get_table: bool = True,):
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
        if "volume" not in lst_com.columns:
            lst_com["volume"] = np.nan
        if "dividend" not in lst_com.columns:
            lst_com["dividend"] = np.nan
        if "table" not in lst_com.columns:
            lst_com["table"] = np.nan
        lst_com.to_csv(self.path_all_com, index=False)
        
        if reverse:
            lst_com = lst_com[::-1]
        for i in lst_com.index:
            id_company = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if check == "Done":
                error = False
                col = None
                try:
                    if bool_get_volume and lst_com["volume"][i] != "Done":
                        col =  "volume"
                        get_volume(id_company, self.path_save, save_file=True)
                    if bool_get_table and lst_com["table"][i] != "Done":
                        col = "table"
                        get_table(id_company, self.path_save, save_file=True)
                    if bool_get_dividend and lst_com["dividend"][i] != "Done":
                        col = "dividend"
                        dividendClass = GetDividend(path_save=self.path_save)
                        dividendClass.get_dividend(id_company, save_file=True)
                except:
                    print("Error: ", id_company)
                    error = True
                    pass
                    
                if col != None:
                    lst_com_ = pd.read_csv(self.path_all_com)
                    if reverse:
                        lst_com_ = lst_com_[::-1]

                    if error:
                        lst_com_[col][i] = "False"
                    else:
                        lst_com_[col][i] = "Done"
                    lst_com_.sort_index(inplace=True)
                    lst_com_.to_csv(self.path_all_com, index=False)
                
            