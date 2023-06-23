import pandas as pd
import numpy as np
import time, os
from src.get_volume import get_volume
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

    def save_dividendShares(self, id_company, done):
        try:
            df = pd.read_csv("docs/DividendShares.csv")
            # print(df)
        except:
            df = pd.DataFrame(columns = ['Symbol', 'DividendShares'])

        if str(id_company) not in df['Symbol'].values:
            # print(df['Symbol'].values)
            df.loc[(len(df))] =[str(id_company), done]
        else:
            df.loc[df['Symbol'] == str(id_company), 'DividendShares'] = done

        df = df.drop(df.loc[df['Symbol'] == 'Total'].index)
        df.loc[(len(df))] = ['Total', (df['DividendShares']== "Done").sum()]
        df.to_csv('docs/DividendShares.csv', index = False)

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
                error = []
                col = []
                if bool_get_volume and lst_com["volume"][i] != "Done":
                    try:
                        get_volume(id_company, self.path_save, save_file=True)
                        col.append("volume")
                    except:
                        error.append("volume")

                if bool_get_table and lst_com["table"][i] != "Done":
                    try:
                        get_table(id_company, self.path_save, save_file=True)
                        col.append("table")
                    except:
                        error.append("table")

                if bool_get_dividend and lst_com["dividend"][i] != "Done":
                    try:
                        dividendClass = GetDividend(path_save=self.path_save)
                        dividendClass.get_dividend(id_company, save_file=True)
                        col.append("dividend")
                    except:
                        error.append("dividend")
                    
                lst_com_ = pd.read_csv(self.path_all_com)
                if reverse:
                        lst_com_ = lst_com_[::-1]

                for col_ in col:
                    lst_com_[col_][i] = "Done"
                    if col_ == "dividend":
                        self.save_dividendShares(id_company, "Done")

                for error_ in error:
                    print(f"Error: {id_company}- {error_}")
                    lst_com_[error_][i] = "False"
                    if error_ == "dividend":
                        self.save_dividendShares(id_company, "False")

                lst_com_.sort_index(inplace=True)
                lst_com_.to_csv(self.path_all_com, index=False)
                
            