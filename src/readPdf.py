import pandas as pd
import numpy as np
from src.volume import GetVolume
from src.get_table import GetTable
from src.dividend import GetDividend

class ReadPdf():
    def __init__(
        self,
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        ):
        self.path_all_com = path_all_com
        self.path_save = path_save

    def saveDividendShares(self, id_company, state):
        """
        Parameters
        ----------
        id_company : int
        state : str
        
        Return
        ----------
            list dividend_shares
        """
        try:
            df = pd.read_csv("docs/DividendShares.csv")
        except:
            df = pd.DataFrame(columns = ['Symbol', 'DividendShares'])

        if str(id_company) not in df['Symbol'].values:
            df.loc[(len(df))] =[str(id_company), state]
        else:
            df.loc[df['Symbol'] == str(id_company), 'DividendShares'] = state

        df = df.drop(df.loc[df['Symbol'] == 'Total'].index)
        df.loc[(len(df))] = ['Total', (df['DividendShares']== "Done").sum()]
        df.to_csv('docs/DividendShares.csv', index = False)

    def getAllCom(self, 
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
        bool_get_volume : bool
            get volume
        bool_get_dividend : bool
            get dividend
        bool_get_table : bool
            get table
        
        Returns
        -------
        None
        """
        lst_com = pd.read_csv(self.path_all_com)

        for col_temp in ["check", "volume", "dividend", "table"]:
            if col_temp not in lst_com.columns:
                lst_com[col_temp] = np.nan
        
        lst_com.to_csv(self.path_all_com, index=False)
        
        if reverse: 
            lst_com = lst_com[::-1]
        

        for i in lst_com.index:
<<<<<<< HEAD
            id_company = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if check == "Done":
                error = [] # list error_name
                col = [] # list column_name have finished
=======
                id_company = lst_com["Symbol"][i]
            # check = lst_com["check"][i]
            # if check == "Done":
                error = []
                col = []
>>>>>>> 19d13d01ab44af1255ac171e6e056fb2d17e0fc3
                if bool_get_volume and lst_com["volume"][i] != "Done":
                    try:
                        get_volume = GetVolume(path_save=self.path_save)
                        get_volume.getVolume(id_company, save_file=True)
                        col.append("volume")
                    except:
                        error.append("volume")

                if bool_get_table and lst_com["table"][i] != "Done":
                    try:
                        getTableClass = GetTable(path_save = self.path_save)
                        getTableClass.getTable(id_company, save_file = True)
                        col.append("table")
                    except:
                        error.append("table")

                if bool_get_dividend and lst_com["dividend"][i] != "Done":
                    try:
                        dividendClass = GetDividend(path_save=self.path_save)
                        dividendClass.getDividend(id_company, save_file=True)
                        col.append("dividend")
                    except:
                        error.append("dividend")
                    
                lst_com_ = pd.read_csv(self.path_all_com)
                if reverse:
                        lst_com_ = lst_com_[::-1]

                for col_ in col:
                    lst_com_[col_][i] = "Done"
                    if col_ == "dividend":
                        self.saveDividendShares(id_company, "Done")

                for error_ in error:
                    print(f"Error: {id_company}- {error_}")
                    lst_com_[error_][i] = "False"
                    if error_ == "dividend":
                        self.saveDividendShares(id_company, "False")

                lst_com_.sort_index(inplace=True)
                lst_com_.to_csv(self.path_all_com, index=False)
