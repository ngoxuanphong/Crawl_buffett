import pdfplumber
import os
import re
import pandas as pd
import numpy as np

pl_text = [
    "四半期連結損益及び包括利益計算書",
    "四半期連結損益計算書",
    "四半期連結損益及び包括利益計算書",
    "連結損益及び包括利益計算書",
    "連結損益計算書",
    '損益計算書'
]

bs_text = ["四半期連結貸借対照表", "連結貸借対照表", "連結財政状態計算書", '貸借対照表'] 


def find_header(pdf, page_id: int, n_cols=3):
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


def check_str(text, lst_str):
    for s in lst_str:
        idx = text.find(s)
        if idx != -1:
            return idx < text.find("単位")
    return False


def convert_text_table(text, n_cols=3):
    lst_rows = text.split("\n")
    lst_table = []
    for r in lst_rows:
        row_ = r.split(" ")
        row = []
        for s in row_:
            if "※" not in s:
                row += [s]

        if len(row) < n_cols:
            row += [None] * (n_cols - len(row))
        elif len(row) > n_cols:
            row = [None] * n_cols
        lst_table += [row]
    return lst_table


def extract_data_pdf_bs(
    pdf, lst_table=[], page_id=0, type_data="find_keyword", lst_str=[]
):
    page = pdf.pages[page_id]
    text = page.extract_text()
    text_ = text.replace(" ", "")

    if type_data == "find_keyword":
        find_key = check_str(text_, lst_str)
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
            lst_table += convert_text_table(table_text, n_cols)
            return lst_table, n_cols, True
    return lst_table, n_cols, False


def extract_data_pdf_pl(
    pdf, lst_table=[], page_id=0, type_data="find_keyword", lst_str=[]
):
    page = pdf.pages[page_id]
    text = page.extract_text()
    text_ = text.replace(" ", "")

    if type_data == "find_keyword":
        find_key = check_str(text_, lst_str)
    if type_data == "avoid_keyword":
        try:
            if int(text_[1]) : # vị trí này là số (thường là 3)
                find_key = False
            else:
                find_key = True
        except:
            idx = text_.find("\n")
            try:
                if int(text_[idx + 2]): #vị trí này là số (thường là 3)
                    find_key = False
                else:
                    find_key = True
            except:
                find_key = True

    n_cols = 0

    if find_key == True:
        table_text = ""
        if text.find("売上高") != -1 and type_data == "find_keyword":
            # print(text.find("売上高"))
            table_text = text[text.find("売上高") :]
        else:
            for str_key in ["四半期純利益", '営業外費用', "当期純利益", "特別利益", "その他の包括利益"]:
                if text.find(str_key) != -1:
                    text1 = text[: text.find(str_key)]
                    table_text = text[text1.rfind("\n") + 1 :]
                    break
        
        # Tìm số cột
        COUNT_ = 5
        # print(table_text)
        if table_text.count('\n') > 5:
            for str in table_text.split("\n")[:-1]:  # không tính phần ghi số trang
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
            lst_table += convert_text_table(table_text, n_cols)
            return lst_table, n_cols, True
    return lst_table, n_cols, False


def extract_pdf(path_file, type_):
    pdf = pdfplumber.open(path_file)
    if type_ == "bs":
        key = bs_text
        for page_id in range(len(pdf.pages)):
            lst_table, n_cols, _ = extract_data_pdf_bs(
                pdf,
                lst_table=[],
                page_id=page_id,
                type_data="find_keyword",
                lst_str=key,
            )
            if _ == True:
                lst_col = find_header(pdf, page_id=page_id, n_cols=n_cols)
                break
        
        while True:
            # print(page_id)
            lst_table, n_cols, _ = extract_data_pdf_bs(
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
        # print(lst_table)
        # print(lst_col)
        df = pd.DataFrame(lst_table, columns=lst_col)
        # df[df[df.columns[0]] != '―']
        return df.replace("", None)

    if type_ == "pl":
        key = pl_text
        for page_id in range(len(pdf.pages)):
            lst_table, n_cols, _ = extract_data_pdf_pl(
                pdf,
                lst_table=[],
                page_id=page_id,
                type_data="find_keyword",
                lst_str=key,
            )
            if _ == True:
                lst_col = find_header(pdf, page_id=page_id, n_cols=n_cols)
                break

        while True:
            # print(page_id)
            lst_table, n_cols, _ = extract_data_pdf_pl(
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
        # print(lst_table)
        # print(lst_col)
        df = pd.DataFrame(lst_table, columns=lst_col)
        # df[df[df.columns[0]] != '―']
        return df.replace("", None)

def get_table_from_pdf(id_company, path_save, file, type_ = 'bs'):
    path_file = path_save + f'Data/{id_company}/PDF/{file}'
    df_table = extract_pdf(path_file, type_)
    return df_table 

def get_table(id_company, path_save, save_file = False, return_check = True):
    df_time = pd.read_csv(path_save + f'Data/{id_company}/docs/link.csv')
    checklist = []
    print(f'Get table of {id_company}')
    for quy in ['Q1', 'Q2', 'Q3', 'Q4']:
        for id in df_time.index:
            year = df_time[f'Year'][id]
            check_file = False

            for file in os.listdir(path_save + f'Data/{id_company}/PDF'):
                if file.startswith(f'{year}_{quy}') and '(訂正)' not in file and 'ocr' not in file:
                    check_file = True
                    check_bs = 'Done'
                    try:
                        df_bs = get_table_from_pdf(id_company, path_save, file, type_= 'bs')
                        if save_file:
                            path = path_save + f'Data/{id_company}/table_bs'
                            # Kiểm tra nếu thư mục chưa tồn tại
                            if not os.path.exists(path):
                                # Tạo thư mục
                                os.makedirs(path)
                            df_bs.to_csv(path_save + f'Data/{id_company}/table_bs/{year}_{quy}.csv', index=False)
                    except:
                        check_bs = 'B'

                    check_pl = 'Done'
                    try:
                        df_pl = get_table_from_pdf(id_company, path_save, file, type_= 'pl')
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
    if return_check:
        return df_checklist



# 9997 Do dịch lỗi: (cid:17082)(cid:17044)(cid:17062)(cid:17079)(cid:17029)(cid:17128)...
# 9995 Văn bản lỗi, các chữ thưa nhau, sai số cột
#      Đã fix lỗi không tìm điểm dừng khi lấy bảng pl--  ok
#      Bảng quá ngắn chứng tỏ sai (lỗi do tìm thấy từ khóa ở trang k phải trang cần tìm)
# 9994: 2008 Q1 Dạng bảng khác, 
#       2016 Q4: dịch lỗi: không ra data bảng

#9990: 2013 Q1: Lỗi bảng ngắn -> tính luôn phần số trang - 7 - -> số cột = 3 sai: 
#       2011 Q4 Thieu keyword