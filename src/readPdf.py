from datetime import timedelta
import pandas as pd
import numpy as np
from src.ocrPdf import GetVolume, GetTable, GetDividend
import os
import shutil


class ReadPdf():
    """
    Read pdf file and move to driver
    
    Parameters
    ----------
    path_all_com : str
        path to list company
        default: "docs/List_company_23052023 - Listing.csv"
    path_save : str
        path to save data
        default: "Data"
    PATH_DRIVER : str
        path to driver
        default: "I:/My Drive/6_2023/DoneJapan"

        """
    def __init__(
        self,
        path_all_com="docs/List_company_23052023 - Listing.csv",
        path_save="Data",
        PATH_DRIVER = "I:/My Drive/6_2023/DoneJapan",
        ):
        self.path_all_com = path_all_com
        self.path_save = path_save
        self.PATH_DRIVER = PATH_DRIVER
        self.makeFolder()

    def makeFolder(self):
        """
        Make folder to save data
        """
        PATH_DRIVER = self.PATH_DRIVER
        self.PATH_IS = PATH_DRIVER + '/IncomeStatement/'
        self.PATH_BS = PATH_DRIVER + '/BalanceSheet/'
        self.PATH_volume = PATH_DRIVER + '/volume/'
        self.PATH_dividend = PATH_DRIVER + '/dividend/'
        os.makedirs(self.PATH_IS, exist_ok=True)
        os.makedirs(self.PATH_BS, exist_ok=True)
        os.makedirs(self.PATH_volume, exist_ok=True)
        os.makedirs(self.PATH_dividend, exist_ok=True)

    def saveDividendShares(self, symbol, state):
        """
        Parameters
        ----------
        symbol : int
        state : str
        
        Return
        ----------
            list dividend_shares
        """
        try:
            df = pd.read_csv("docs/DividendShares.csv")
        except:
            df = pd.DataFrame(columns = ['Symbol', 'DividendShares'])

        if str(symbol) not in df['Symbol'].values:
            df.loc[(len(df))] =[str(symbol), state]
        else:
            df.loc[df['Symbol'] == str(symbol), 'DividendShares'] = state

        df = df.drop(df.loc[df['Symbol'] == 'Total'].index)
        df.loc[(len(df))] = ['Total', (df['DividendShares']== "Done").sum()]
        df.to_csv('docs/DividendShares.csv', index = False)

    def getAllCom(self, 
                    reverse: bool = False,
                    bool_get_volume: bool = True,
                    bool_get_dividend: bool = True,
                    bool_get_table: bool = True,
                    list_symbol: list = []):
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
        if list_symbol != []:
            for symbol in list_symbol:
                try:
                    if bool_get_volume:
                        get_volume = GetVolume(path_save=self.path_save)
                        get_volume.getVolume(symbol, save_file=True)
                except Exception as e:
                    print(f"Error: {symbol}", e)
                try:
                    if bool_get_table:
                        getTableClass = GetTable(path_save = self.path_save)
                        getTableClass.getTable(symbol, save_file = True)
                except Exception as e:
                    print(f"Error: {symbol}", e)
                try:
                    if bool_get_dividend:
                        dividendClass = GetDividend(path_save=self.path_save)
                        dividendClass.getDividend(symbol, save_file=True)
                except Exception as e:
                    print(f"Error: {symbol}", e)
            return

        self.reverse = reverse

        lst_com = pd.read_csv(self.path_all_com)

        for col_temp in ["check", "volume", "dividend", "table"]:
            if col_temp not in lst_com.columns:
                lst_com[col_temp] = np.nan
        
        if self.reverse: 
            lst_com = lst_com[::-1]

        for i in lst_com.index:
            symbol = lst_com["Symbol"][i]
            check = lst_com["check"][i]
            if check == "Done":
                if bool_get_volume and lst_com["volume"][i] != "Done":
                    try:
                        get_volume = GetVolume(path_save=self.path_save)
                        get_volume.getVolume(symbol, save_file=True)
                        self.saveData('Done', i, 'volume')
                    except Exception as e:
                        print(f"Error: {symbol}- volume", e)

                if bool_get_table and lst_com["table"][i] != "Done":
                    try:
                        getTableClass = GetTable(path_save = self.path_save)
                        getTableClass.getTable(symbol, save_file = True)
                        self.saveData('Done', i, 'table')
                    except Exception as e:
                        print(f"Error: {symbol}- table", e)

                if bool_get_dividend and lst_com["dividend"][i] != "Done":
                    try:
                        dividendClass = GetDividend(path_save=self.path_save)
                        dividendClass.getDividend(symbol, save_file=True)
                        self.saveData('Done', i, 'dividend')
                    except Exception as e:
                        print(f"Error: {symbol}- dividend", e)
                    
                    

    def saveData(self, msg, id, col):
        """
        Save data to csv

        Parameters
        ----------
        msg : str
            message
        id : int
            id company
        col : str
            column name
        
        Returns
        -------
        None
        """

        lst_com_ = pd.read_csv(self.path_all_com)
        if self.reverse:
                lst_com_ = lst_com_[::-1]

        lst_com_[col][id] = msg
        lst_com_.sort_index(inplace=True)
        lst_com_.to_csv(self.path_all_com, index=False)

    def sortDate(self, df, type_ = 'volume'):
        """
        Sort date

        Parameters
        ----------
        df : DataFrame
            data
        type_ : str
            type of data

        Returns
        -------
        df : DataFrame
            data
        """

        if type_ == 'volume':
            df['Time'] = pd.to_datetime(df['Time'], format='%Y_%m_%d', errors='coerce')
        else:
            df['Time'] = pd.to_datetime(df['Time'], format='%d_%m_%Y', errors='coerce')
        df.sort_values(by=['Time'], inplace=True)
        df['Time'] = df['Time'].dt.strftime('%d/%m/%Y')
        return df

    def delDate(self, time, date):
        """
        Trừ đi 1 năm, Hàm này bỏ, không dùng đến

        Parameters
        ----------
        time : str
            time
        date : str
            date
        Returns
        -------
        date : str
            date
        """

        if pd.isna(date):
            return date
        if 'Q1' in time or 'Q2' in time:
            date = pd.to_datetime(date, format='%Y_%m_%d', errors='coerce')
            date = date - timedelta(days=365)
            date = date.strftime('%Y_%m_%d')
        return date

    def moveVolume(self, symbol):
        df = pd.read_csv(fr'Data\{symbol}\docs\volume.csv')
        # if not os.path.exists(fr'Data\{symbol}\docs\check.csv'):
        #     df['date'] = df[['time', 'date']].apply(lambda x: self.delDate(x['time'], x['date']), axis=1)
        df['volume'] = df['vol1'] - df['vol2']
        df = df[['date', 'volume']]
        df.dropna(how = 'all', inplace=True)
        df.rename(columns={'date': 'Time', 'volume': 'Volume'}, inplace=True)
        df = self.sortDate(df, type_ = 'volume')
        df.to_csv(fr'{self.PATH_volume}{symbol}.csv', index = False)
        return df

    def moveDividend(self, symbol):
        """
        Save dividend to drive

        Parameters
        ----------
        symbol : str
            symbol of company
        """

        df = pd.read_csv(fr'Data\{symbol}\docs\dividend.csv')
        df_done = pd.DataFrame(columns = ['Time', 'Stock', 'Money', 'Time2'])
        df_done['Time'] = df[['time_split_Q1', 'time_split_Q2', 'time_split_Q3', 'time_split_Q4']].stack(dropna=False).reset_index(drop=True)
        df_done['Time'] = df_done['Time'].str.replace("['", '').str.replace("']", '')
        df_done['Money'] = df[['Q1', 'Q2', 'Q3', 'Q4']].stack(dropna=False).reset_index(drop=True)
        for q in  ['Q1', 'Q2', 'Q3', 'Q4']:
            df[q] = df['Year'].astype(str) + '_' + q
        df_done['Time2'] = df[['Q1', 'Q2', 'Q3', 'Q4']].stack(dropna=False).reset_index(drop=True)
        df_done.replace('－', np.nan, inplace=True)
        df_done.replace('―', np.nan, inplace=True)
        df_done.replace('-', np.nan, inplace=True)
        df_done.replace('—', np.nan, inplace=True)
        df_done.replace('一', np.nan, inplace=True)
        df_done.replace('=', np.nan, inplace=True)
        df_done.dropna(inplace=True, thresh=2)
        df_done = self.sortDate(df_done, type_ = 'dividend')
        df_done.to_csv(fr'{self.PATH_dividend}{symbol}.csv', index = False)
        return df_done


    def moveFinancial(self, symbol):
        """
        Save financial to drive

        Parameters
        ----------
        symbol : str
            symbol of company
        """

        path_bs = rf'Data\{symbol}\table_bs'
        path_pl = rf'Data\{symbol}\table_pl'
        for file in os.listdir(path_bs):
            if file.endswith('Q4.csv'):
                os.makedirs(self.PATH_BS + '/' + str(symbol), exist_ok=True)
                shutil.copy(path_bs + '/' + file, self.PATH_BS + '/' + str(symbol) + '/' + file)
        for file in os.listdir(path_pl):
            if file.endswith('Q4.csv'):
                os.makedirs(self.PATH_IS + str(symbol), exist_ok=True)
                shutil.copy(path_pl + '/' + file, self.PATH_IS + '/' + str(symbol) + '/' + file)


    def moveToDrive(self
                    , move_volume = False
                    , move_dividend = False
                    , move_financial = False
                    , list_symbol = []):
        """
        Move data to drive

        Parameters
        ----------
        move_volume : bool
            move volume data
        move_dividend : bool
            move dividend data
        move_financial : bool
            move financial data

        Returns
        -------
        None
        """
        if list_symbol != []:
            for symbol in list_symbol:
                if move_volume:
                    try:
                        self.moveVolume(symbol)
                    except Exception as e:
                        print(symbol, e)

                if move_financial:
                    try:
                        self.moveFinancial(symbol)
                    except Exception as e:
                        print(symbol, e)

                if move_dividend:
                    try:
                        self.moveDividend(symbol)
                    except Exception as e:
                        print(symbol, e)
            return
        
        df = pd.read_csv(self.path_all_com)

        for id in df.index:
            symbol = df['Symbol'][id]
            if df['check'][id] == 'Done':
                if os.path.exists(fr'Data\{symbol}\docs\volume.csv') and move_volume:
                    try:
                        self.moveVolume(symbol)
                    except Exception as e:
                        print(symbol, e)

                if os.path.exists(fr'Data\{symbol}\docs\dividend.csv') and move_dividend:
                    try:
                        self.moveDividend(symbol)
                    except Exception as e:
                        print(symbol, e)
                
                if move_financial:
                    try:
                        self.moveFinancial(symbol)
                    except Exception as e:
                        print(symbol, e)
