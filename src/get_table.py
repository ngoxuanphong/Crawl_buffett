import pdfplumber
import os
import re
import pandas as pd
import numpy as np

class GetTable:
    pl_key_word = [
    "四半期連結損益及び包括利益計算書",
    "四半期連結損益計算書",
    "四半期連結損益及び包括利益計算書",
    "連結損益及び包括利益計算書",
    "連結損益計算書",
    '損益計算書'
    ]

    bs_key_word = ["四半期連結貸借対照表", "連結貸借対照表", "連結財政状態計算書", '貸借対照表'] 

    def __init__(self,
            path_save:str = '',
            ):
        self.path_save = path_save
    
    def findHeader(self, pdf, page_id: int, n_cols=3):
        """
        Parameters
        ----------
        pdf : 
        page_id : int
        n_cols : int
            Số lượng cột

        Return
        ----------
        list[str]
            header of table
        """
        page = pdf.pages[page_id]
        text = page.extract_text()
        DON_VI = "単位"

        idx_dv = text.find(DON_VI)
        if idx_dv >= 0:
            text1 = text[idx_dv:]
            ## Tim don vi
            Yen_unit = text1[3 : text1.find("\n") - 1]
            ## Tim field
            text2 = text1[text1.find("\n") + 1 :]
            text3 = text2[: text2.find("\n")]
            text3 = text3.split(" ")

            if len(text3) != n_cols - 1:
                return [Yen_unit] + ["B"] * (n_cols - 1)
            return [Yen_unit] + text3

        else:
            return ["N/A"] * n_cols

    def checkStr(self, text, lst_str):
        """
        Parameters
        -----------
        text : str
            text của trang đang xét
        lst_str : list[str]
            Danh sách key word

        Return
        -----------
        bool :
            Trang có key_word cần tìm
        """
        for s in lst_str:
            idx = text.find(s)
            if idx != -1:
                return idx < text.find("単位") # Chỉ tính key word trong phần đầu của trang (nằm trước DON_VI)
        return False

    def convertTextTable(self, text, n_cols=3):
        """
        Parameters
        -----------
        text : str
            text của trang đang xét
        n_cols : int
            số lượng cột

        Return
        -----------
        list
            convert text -> table
        """
        lst_rows = text.split("\n")
        lst_table = []
        for r in lst_rows:
            row_ = r.split(" ")
            row = []
            for s in row_:
                if "※" not in s: # Loại bỏ các phần có kí tự này
                    row += [s]

            if len(row) < n_cols:
                row += [None] * (n_cols - len(row))
            elif len(row) > n_cols:
                row = [None] * n_cols
            lst_table += [row]
        return lst_table

    def extractDataPdfBs(self, 
        pdf, lst_table=[], page_id=0, type_data="find_keyword", lst_str=[]
    ):
        """
        Parameters
        -----------
        pdf :
        lst_table : list
            default is a empty list
        page_id :
            default is 0
        type_data : str
            default is "find_keyword" : Dạng tìm kiếm
        lst_str : list[str]
            list key word

        Return
        -----------
        bool :
            Trang có key_word cần tìm
        """
        page = pdf.pages[page_id]
        text = page.extract_text()
        text_ = text.replace(" ", "")

        if type_data == "find_keyword":
            find_key = self.checkStr(text_, lst_str)
        if type_data == "avoid_keyword":
            try:
                if int(text_[1]) == 2:
                    find_key = False
                else:
                    find_key = True
            except:
                idx = text_.find("\n")
                try:
                    if int(text_[idx + 2]) == 2:
                        find_key = False
                    else:
                        find_key = True
                except:
                    find_key = True

            # find_key = False
            # if text_[1: 3] == '単位':
            #     find_key = True
            # idx = text_.find('\n')
            # if text_[idx + 2: idx + 4] == '単位':
            #     find_key = True

        n_cols = 0
        if find_key == True:
            table_text = ""
            if type_data == "find_keyword":
                table_text = text[text.find("資産の部") :]
            if type_data == "avoid_keyword":
                if text.find("負債の部") != -1:
                    table_text = text[text.find("負債の部") :]
                elif text.find("資産の部") != -1:
                    table_text = text[text.find("資産の部") :]

            # Tìm số cột
            if table_text.count('\n') > 5: #bảng đủ ngắn chứng tỏ bị lỗi
                COUNT_ = 10
                for str in table_text.split("\n")[:-1]:  # find count columns by 10 first rows
                    COUNT_ -= 1
                    row_ = str.split(" ")
                    row = []
                    for s in row_:
                        if "※" not in s:
                            row += [s]

                    n_cols = max(n_cols, len(row))
                    if COUNT_ == 0:
                        break

                # find table
                if n_cols > 5:
                    return 10/0 ### tạo ra bug để báo lỗi khi số cột sai >5
                lst_table += self.convertTextTable(table_text, n_cols)
                return lst_table, n_cols, True
        return lst_table, n_cols, False

    def extractDataPdfPl(self, 
        pdf, lst_table=[], page_id=0, type_data="find_keyword", lst_str=[]
    ):
        """
        Parameters
        -----------
        pdf :
        lst_table : list
            default is a empty list
        page_id :
            default is 0
        type_data : str
            default is "find_keyword" : Dạng tìm kiếm
        lst_str : list[str]
            list key word
            
        Return
        -----------
        bool :
            Trang có key_word cần tìm
        """
        page = pdf.pages[page_id]
        text = page.extract_text()
        text_replace = text.replace(" ", "")

        # Xét dấu hiệu trong trang bắt đầu có bảng
        if type_data == "find_keyword":
            find_key = self.checkStr(text_replace, lst_str)

        # Xét dấu hiệu trong trang kết thúc của bảng 
        if type_data == "avoid_keyword": 
            try:
                if int(text_replace[1]) : # vị trí này là số (thường là 3)
                    find_key = False# Tìm vị trí kết thúc để lấy bảng
                else:
                    find_key = True
            except:
                idx = text_replace.find("\n")
                try:
                    if int(text_replace[idx + 2]): #vị trí này là số (thường là 3)
                        find_key = False
                    else:
                        find_key = True
                except:
                    find_key = True

        n_cols = 0 # Số cột
        if find_key == True:
            table_text = ""
            # Đối với trang đầu tiên có bảng
            if text.find("売上高") != -1 and type_data == "find_keyword":
                # print(text.find("売上高"))
                table_text = text[text.find("売上高") :]

            # Đối với trang tiếp theo chứa bảng đó
            else:
                for str_key in ["四半期純利益", '営業外費用', "当期純利益", "特別利益", "その他の包括利益"]:
                    if text.find(str_key) != -1:
                        text1 = text[: text.find(str_key)]
                        table_text = text[text1.rfind("\n") + 1 :]
                        break
            
            # Tìm số cột
            COUNT_ = 5 # Xét 5 dòng đầu tiên xem -> tìm n_cols
            if table_text.count('\n') > 5: # Quá ngắn nhiều khả năng không phải bảng
                for str in table_text.split("\n")[:-1]:  # không tính phần ghi số trang (dòng cuối là ghi số trang)
                    COUNT_ -= 1
                    row_ = str.split(" ")
                    row = []
                    for s in row_:
                        if "※" not in s:
                            row += [s]

                    n_cols = max(n_cols, len(row))
                    if COUNT_ == 0:
                        break

                # find table
                if n_cols > 5:
                    return 10/0 ### tạo ra bug để báo lỗi khi số cột sai >5
                
                lst_table += self.convertTextTable(table_text, n_cols)
                return lst_table, n_cols, True
        return lst_table, n_cols, False

    def extractPdf(self, path_file, type_):
        """
        Parameters
        -----------
        path_file : str
        type_ : str
            'bs' or 'pl'
            
        Return
        -----------
        DataFrame :
            get table
        """
        pdf = pdfplumber.open(path_file)
        if type_ == "bs":
            key = self.bs_key_word

            # Tìm trang đầu tiên chứa bảng cần lấy
            for page_id in range(len(pdf.pages)):
                lst_table, n_cols, _ = self.extractDataPdfBs(
                    pdf,
                    lst_table=[],
                    page_id=page_id,
                    type_data="find_keyword",
                    lst_str=key,
                )
                if _ == True:
                    lst_col = self.findHeader(pdf, page_id=page_id, n_cols=n_cols)
                    break

            # Lấy dữ liệu bảng đó từ các trang tiếp theo
            while True:
                # print(page_id)
                lst_table, n_cols, _ = self.extractDataPdfBs(
                    pdf,
                    lst_table=lst_table,
                    page_id=page_id + 1,
                    type_data="avoid_keyword",
                    lst_str=[],
                )
                if _ == True:
                    page_id += 1
                else:
                    break
            
            df = pd.DataFrame(lst_table, columns=lst_col)
            # df[df[df.columns[0]] != '―']
            return df.replace("", None)

        if type_ == "pl":
            key = self.pl_key_word

            # Tìm trang đầu tiên chứa bảng cần lấy
            for page_id in range(len(pdf.pages)):
                lst_table, n_cols, _ = self.extractDataPdfPl(
                    pdf,
                    lst_table=[],
                    page_id=page_id,
                    type_data="find_keyword",
                    lst_str=key,
                )
                if _ == True:
                    lst_col = self.findHeader(pdf, page_id=page_id, n_cols=n_cols)
                    break

             # Lấy dữ liệu bảng đó từ các trang tiếp theo
            while True:
                # print(page_id)
                lst_table, n_cols, _ = self.extractDataPdfPl(
                    pdf,
                    lst_table=lst_table,
                    page_id=page_id + 1,
                    type_data="avoid_keyword",
                    lst_str=[],
                )
                if _ == True:
                    page_id += 1
                else:
                    break
            
            df = pd.DataFrame(lst_table, columns=lst_col)
            # df[df[df.columns[0]] != '―']
            return df.replace("", None)

    def getTableFromPdf(self, 
                        id_company, 
                        file, type_ = 'bs'):
        """
        Parameters
        -----------
        id_company : int
        file : str
            file name
        type_ : str
            'bs' or 'pl'
            
        Return
        -----------
        DataFrame :
            get table
        """
        path_file = self.path_save + f'Data/{id_company}/PDF/{file}'
        df_table = self.extractPdf(path_file, type_)
        return df_table 

    def getTable(self, 
                 id_company, 
                 return_df = False,
                 save_file = True):
        """
        Parameters
        -----------
        id_company : int
            id of company default is 1301
        return_df : bool
            return dataframe of data default is False
        save_file : bool
            save dataframe of data default is True
        """
        path_save = self.path_save
        df_time = pd.read_csv(path_save + f'Data/{id_company}/docs/link.csv')
        checklist = []

        print(f'Get table of {id_company}')
        for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
            for id in df_time.index:
                if 'year' in df_time.columns:
                    year = df_time[f"Year"][id]
                else:
                    year = df_time.iloc[id, 0][2:6]
                check_file = False

                for file in os.listdir(path_save + f'Data/{id_company}/PDF'):
                    if file.startswith(f'{year}_{quy}') and '(訂正)' not in file and 'ocr' not in file:
                        check_file = True
                        # get bs-----------------
                        check_bs = 'Done'
                        try:
                            df_bs = self.getTableFromPdf(id_company, file, type_= 'bs')
                            if save_file:
                                path = path_save + f'Data/{id_company}/table_bs'
                                # Kiểm tra nếu thư mục chưa tồn tại
                                if not os.path.exists(path):
                                    # Tạo thư mục
                                    os.makedirs(path)
                                df_bs.to_csv(path_save + f'Data/{id_company}/table_bs/{year}_{quy}.csv', index=False)
                        except:
                            check_bs = 'B'

                        # get pl------------------
                        check_pl = 'Done'
                        try:
                            df_pl = self.getTableFromPdf(id_company, file, type_= 'pl')
                            if save_file:
                                path = path_save + f'Data/{id_company}/table_pl'
                                # Kiểm tra nếu thư mục chưa tồn tại
                                if not os.path.exists(path):
                                    # Tạo thư mục
                                    os.makedirs(path)
                                df_pl.to_csv(path_save + f'Data/{id_company}/table_pl/{year}_{quy}.csv', index=False)
                        except:
                            check_pl = 'B'
                        checklist += [[f'{year}_{quy}', check_bs, check_pl]]

                if check_file == False:
                    checklist += [[f'{year}_{quy}', 'N/A', 'N/A']]

        df_checklist = pd.DataFrame(checklist, columns=['Time', 'get_bs', 'get_pl'])
        df_checklist.to_csv(path_save + f'Data/{id_company}/docs/checklist_get_table.csv', index = False)
        if return_df:
            return df_checklist
