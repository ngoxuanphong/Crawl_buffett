import pandas as pd
import numpy as np
import os, re
import shutil

import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
# from pandas.core.common import SettingWithCopyWarning
# warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import pandas

LST_SUM_FEATURE = [
                    ['Short term receivables',
                    'STR_1',
                    'STR_2',
                    'STR_3',
                    'STR_4',
                    'STR_5',
                    'STR_6',
                    'STR_7',
                    'STR_8',
                    'STR_9',
                    'STR_10',
                    'STR_11',
                    'STR_12',
                    'STR_13',
                    'STR_14',
                    'STR_15',
                    'STR_16',
                    'STR_17',
                    'STR_18',
                    'STR_19'],
                    ['Total Inventories',
                    'TotalInventories_1',
                    'TotalInventories_2',
                    'TotalInventories_3',
                    'TotalInventories_4',
                    'TotalInventories_5',
                    'TotalInventories_6',
                    'TotalInventories_7',
                    'TotalInventories_8',
                    'TotalInventories_9',
                    'TotalInventories_10',
                    'TotalInventories_11',
                    'TotalInventories_12',
                    'TotalInventories_13',
                    'TotalInventories_14',
                    'TotalInventories_15',
                    'TotalInventories_16',
                    'TotalInventories_17',
                    'TotalInventories_18',
                    'TotalInventories_19']
                    ]

class ConvertJapanStock():
    def __init__(self,
                 PATH:str = '/content/drive/MyDrive/6_2023/Japan/'):
        """
        Convert data from Financial_2 to Financial_2_F1 and Financial_2_F2

        Parameters
        ----------
        PATH : str, optional
            Path to folder Financial_2, by default '/content/drive/MyDrive/6_2023/Japan/'

        """

        self.PATH = PATH
        self.PATH_FO = f'{self.PATH}/Financial_2/'
        self.PATH_F1 = f'{self.PATH}/Financial_2_F1/'
        self.PATH_F2 = f'{self.PATH}/Financial_2_F2/'
        self.PATH_F3 = f'{self.PATH}/Financial_2_F3/true/'
        self.PATH_F3_FALSE = f'{self.PATH}/Financial_2_F3/false/'

        self.INCOME = 'IncomeStatement'
        self.BALANCE = 'BalanceSheet'

        self.PATH_ALL_COM = f'{self.PATH}List_Company/List_company_23052023.xlsx'
        self.PATH_FEATURE = f'{self.PATH}Checklist/Infor/(Japan)_library.xlsx'
        self.LIST_TYPE_DATA = [self.INCOME, self.BALANCE]
        self.LST_SUM_FEATURE = LST_SUM_FEATURE

        self.makeFolder(f'{self.PATH_F1}/{self.INCOME}')
        self.makeFolder(f'{self.PATH_F1}/{self.BALANCE}')
        self.makeFolder(f'{self.PATH_F2}/{self.INCOME}')
        self.makeFolder(f'{self.PATH_F2}/{self.BALANCE}')
        self.makeFolder(f'{self.PATH_F3}/{self.INCOME}')
        self.makeFolder(f'{self.PATH_F3}/{self.BALANCE}')
        self.makeFolder(f'{self.PATH_F3_FALSE}/{self.INCOME}')
        self.makeFolder(f'{self.PATH_F3_FALSE}/{self.BALANCE}')

        self.makeFolder(f'{self.PATH_F3_FALSE}')


    def deleteFolder(self, path):
        shutil.rmtree(path)


    def makeFolder(self, path):
        os.makedirs(path, exist_ok=True)


    def fillNanColName(self, df):
        """
        Fill nan in column name

        Parameters
        ----------
        df : DataFrame
            DataFrame need to fill nan in column name

        Returns
        -------
        df : DataFrame
            DataFrame after fill nan in column name
        """

        indices = df[df.apply(lambda row: row.count(self,) == 1, axis=1)].index
        index_fill = df[pd.isna(df.iloc[:,0])].index
        for f_id in index_fill:
            for j in range(len(indices)-1):
                if (indices[j] < f_id) and (indices[j+1] > f_id):
                    df.iloc[f_id, 0] = df.iloc[indices[j], 0]
                    break
        return df


    def cutData(self, x):
        """
        Cut data in column Feature

        Parameters
        ----------
        x : str
            Data need to cut

        Returns
        -------
        result : str
            Data after cut
        """

        if pd.isna(x): return x
        result = re.sub(r'\（.*?\）', ' ', x)
        return result.replace(' ', '')


    def renameColumn(self, x):
        """
        Rename column

        Parameters
        ----------
        x : str
            Column name need to rename

        Returns
        -------
        x : str
            Column name after rename

        """
        if x == 'Feature': return x
        x = x.replace('.1', '')
        try:
            return (pd.to_datetime(x) - pd.DateOffset(years=1)).strftime('%Y/%-m/%-d')
        except:
            return x


    def convertF1(self, id_company, PATH_DATA):
        """
        Convert data from Financial_2 to Financial_2_F1

        Parameters
        ----------
        id_company : str
            ID of company
        PATH_DATA : str
            Type of data (IncomeStatement or BalanceSheet)

        Returns
        -------
        df : DataFrame
            DataFrame after convert
        """
        df = pd.read_csv(f'{self.PATH_FO}{PATH_DATA}/{id_company}.csv')
        df = self.fillNanColName(df)

        df = df.replace('－', np.nan)
        df = df.dropna(thresh=2).reset_index(drop = True)

        df.iloc[:, 0] = df.iloc[:, 0].str.replace(' ', '')
        df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x : self.cutData(x))

        df.columns = df.columns.str.replace(' ', '').str.replace('自', '').str.replace('年', '/').str.replace('月', '/').str.replace('日', '') # change time
        df.columns = ['Feature'] + [i[0] for i in df.columns.str.split('至')[1:]] # rename column
        if PATH_DATA == self.BALANCE:
            df = df.rename(columns=lambda x: self.renameColumn(x))
        df['Feature'].replace('', np.nan, inplace = True) # Drop feature nan
        df.dropna(subset = 'Feature', inplace = True)
        df = df.reset_index(drop = True)

        df.to_csv(f'{self.PATH_F1}{PATH_DATA}/{id_company}.csv', index=False)
        return df


    def convertFeature(self, PATH_DATA):
        """
        Convert feature from Financial_2 to Financial_2_F1

        Parameters
        ----------
        PATH_DATA : str
            Type of data (IncomeStatement or BalanceSheet)

        Returns
        -------
        df_feature : DataFrame
            DataFrame after convert
        """
        if PATH_DATA == self.INCOME:
            df_feature = pd.read_excel(self.PATH_FEATURE)
        if PATH_DATA == self.BALANCE:
            df_feature = pd.read_excel(self.PATH_FEATURE, sheet_name='Test_BS')
        df_split =  df_feature['Japan'].str.split(',', expand = True)
        df_feature['Japan'] = df_feature['Japan'].str.replace(' ','')
        df_feature[np.arange(len(df_split.columns))] = df_feature['Japan'].str.split(',', expand = True)
        try:
            df_feature.drop(columns = ['Japan', 'Symbol'], inplace = True)
        except:
            df_feature.drop(columns = ['Japan'], inplace = True)
        return df_feature.reset_index(drop = True)


    def convertF2(self, df_feature, id_company, PATH_DATA):
        """
        Convert data from Financial_2 to Financial_2_F2

        Parameters
        ----------
        df_feature : DataFrame
            DataFrame of feature
        id_company : str
            ID of company
        PATH_DATA : str
            Type of data (IncomeStatement or BalanceSheet)

        Returns
        -------
        df_f2 : DataFrame
            DataFrame after convert

        """
        lst_feature = list(df_feature['English'])
        df = pd.read_csv(f'{self.PATH_F1}{PATH_DATA}/{id_company}.csv')
        for id_col in range(20):
            try:
                df_feature_temp = df_feature[['English', id_col]].rename(columns = {id_col:'Feature'})
                df_merge_temp = pd.merge(df_feature_temp, df, on = 'Feature')
                if id_col == 0:
                    df_f2 = df_merge_temp
                else:
                    df_f2 = pd.concat([df_f2, df_merge_temp]).reset_index(drop = True)
            except:
                break
        lst_data_find = list(df_f2['English'])
        result = list(set(lst_feature).difference(lst_data_find))
        for i in result:
            df_f2.loc[sum(df_f2.index)] = [i] + list(np.full(len(df_f2.columns)-1, -1))
        df_f2 = df_f2.sort_values(by='English', key=lambda x: x.map(dict(zip(lst_feature, range(len(lst_feature)))))).reset_index(drop = True)
        df_f2.to_csv(f'{self.PATH_F2}{PATH_DATA}/{id_company}.csv', index=False)
        return df_f2

    def runF1(self,):
        """
        Run convertF1
        """
        df_all_com = pd.read_excel(self.PATH_ALL_COM)
        for PATH_DATA in self.LIST_TYPE_DATA:
            for symbol in df_all_com['Symbol']:
                try:
                    self.convertF1(symbol, PATH_DATA)
                except Exception as e:
                    print(symbol)
                    print(e)

    def runF2(self,):
        """
        Run convertF2
        """
        df_all_com = pd.read_excel(self.PATH_ALL_COM)
        for PATH_DATA in self.LIST_TYPE_DATA:
            df_feature = self.convertFeature(PATH_DATA)
            for symbol in df_all_com['Symbol']:
                try:
                    self.convertF2(df_feature, symbol, PATH_DATA)
                except Exception as e:
                    print(symbol)
                    print(e)


    def readF2(self,path):
        df = pd.read_csv(path)
        df = df.replace(np.nan, '0').replace('-1', '0')
        df.iloc[:, 2:] = df.iloc[:, 2:].applymap(lambda x: pd.to_numeric(x.replace(',', ''), errors='coerce'))
        return df


    def sumFeatureBalance(self,df):
        for i in range(len(self.LST_SUM_FEATURE)):
            df_short_temp = df[df['English'].isin(self.LST_SUM_FEATURE[i])]
            first_id = df_short_temp.index[0]
            list_data = [df_short_temp.iloc[0, 0], ''] + list(df_short_temp.iloc[:, 2:].sum())
            df.drop(df_short_temp.index, inplace = True)
            df.loc[first_id] = list_data
        return df.sort_index()


    def chooseColumnData(self,df_temp):
        lst_data = np.unique(df_temp.to_numpy())
        if len(lst_data) == 1:
            return lst_data[0]
        if (len(lst_data) == 2) and (0 in lst_data):
            for i in lst_data:
                if i != 0: return i
        return '-------'


    def mergeDF(self, df_temp):
        if len(df_temp.index) == 1: return df_temp
        df_temp.iloc[:, 2:] = df_temp.iloc[:, 2:].apply(lambda y: self.chooseColumnData(y), axis = 0)
        df_temp['Feature'] = np.nan
        df_temp.drop_duplicates(inplace = True)
        return df_temp

    def runF3Company(self,PATH_DATA, id_company):
        df = self.readF2(f'{self.PATH_F2}{PATH_DATA}/{id_company}.csv')
        if PATH_DATA == self.BALANCE:
            df = self.sumFeatureBalance(df)
        df = df.groupby('English', group_keys=False).apply(lambda x: self.mergeDF(x))
        df.sort_index(inplace = True)
        return df

    def runF3(self,):
        df_all_com = pd.read_excel(self.PATH_ALL_COM)
        for PATH_DATA in self.LIST_TYPE_DATA:
            for symbol in df_all_com['Symbol']:
                try:
                    df = self.runF3Company(PATH_DATA, symbol)
                    df.to_csv(f'{self.PATH_F3}{PATH_DATA}/{symbol}.csv', index=False)
                except Exception as e:
                    print(symbol)
                    print(e)

    def makeFalseF3(self, PATH_DATA, 
                    symbol = '1301'):
        PATH_DATA = self.INCOME
        df = pd.read_csv(f'{self.PATH_F3}{PATH_DATA}/{symbol}.csv')
        character = '-------'
        if character in df.values:
            print(df)
            rows = df[df.apply(lambda x: x.astype(str).str.contains(character, case=False)).any(axis=1)]
            df_temp = pd.DataFrame(columns = ['Symbol', 'Type', 'English'])
            df_temp.iloc[:, 2] = rows['English']
            df_temp.iloc[:, 0] = symbol
            df_temp.iloc[:, 1] = PATH_DATA

            df_f3 = pd.read_csv(f'{self.PATH_F3}{PATH_DATA}/{symbol}.csv')
            df_f3.to_excel(f'{self.PATH_F3_FALSE}{PATH_DATA}/{symbol}.xlsx', index=False)
            return df_temp

    def makeFalseF3All(self):
        df_all_com = pd.read_excel(self.PATH_ALL_COM)
        df = pd.DataFrame(columns = ['Symbol', 'Type', 'English'])
        for PATH_DATA in self.LIST_TYPE_DATA:
            for symbol in df_all_com['Symbol']:
                # try:
                    df_temp = self.makeFalseF3(PATH_DATA, symbol)
                    df = pd.concat([df, df_temp])
                # except Exception as e:
                #     print(symbol, '---', e)
        df.to_csv(f'{self.PATH_F3_FALSE}F3.csv', index = False)


# convert = ConvertJapanStock()
# convert.runF3()
# convert.makeFalseF3All()