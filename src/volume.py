import PyPDF2
import re
import os
import pandas as pd
import numpy as np
import warnings
import tabula, camelot
import pandas as pd
import numpy as np
import ocrmypdf
from src.ocrpdf import ocr_pdf

warnings.simplefilter("ignore", UserWarning)


def convert_pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()

    return text


def find_by_re(text2):
    # print(text2)
    text2 = text2.replace(" ", "")
    numbers = re.findall(r"\d{1,3}(?:,\d{3})*", text2)
    # print(numbers)
    filtered_numbers = [
        int(number.replace(",", ""))
        for number in numbers
        if int(number.replace(",", "")) > 3000
    ]
    if len(filtered_numbers) >= 3:
        lst_data_of_time = [filtered_numbers[0], filtered_numbers[2]]
    elif len(filtered_numbers) == 2:
        lst_data_of_time = filtered_numbers
    else:
        lst_data_of_time = [np.nan, np.nan]
    return lst_data_of_time


def convert_text(text1):
    matches = re.finditer("株", text1)
    positions = [match.start() for match in matches]

    text2 = text1[: positions[-1] + 1]
    text2 = text2.replace("③", "\n③").replace(" ,", ",")
    return find_by_re(text2)


def find_row(text):
    text1 = text[text.find("期末発行済株式数") : text.find("期末発行済株式数") + 125]
    text3 = convert_text(text1)
    if text3 == [np.nan, np.nan] and text1 != "":
        text1 = text[text.find("期末発行済株式数") : text.find("期末発行済株式数") + 300]
        text3 = convert_text(text1)
    return text3


def get_data_from_pdf(id_company, year, quy, path_save=""):
    for file in os.listdir(path_save + f"Data/{id_company}/PDF"):
        if file.startswith(f"{year}_{quy}") and "(訂正)" not in file:
            file_name = file
            input_path = path_save + f"Data/{id_company}/PDF/{file_name}"
            text = convert_pdf_to_text(input_path)
            date_volume = file_name[file_name.find("(") + 1 : file_name.find(")")]
            try:
                lst_data_of_time = find_row(text)
            except:
                try:
                    lst_data_of_time = get_vol_table(input_path)
                except:
                    try:
                        path_pdf = input_path.replace(".pdf", "_ocr.pdf")
                        if not os.path.exists(path_pdf):
                            ocr_pdf(input_path)
                        text = convert_pdf_to_text(path_pdf)
                        lst_data_of_time = find_row(
                            text.replace(" ", "").replace(".", ",")
                        )
                    except:
                        lst_data_of_time = ["B", "B"]
            print(f"{year}_{quy}: {lst_data_of_time}")
            return [date_volume] + lst_data_of_time
    return ["N/A", "N/A", "N/A"]


def get_volume(id_company, path_save="", return_df=False, save_file=True):
    df_volume = pd.DataFrame(columns=["time", "time2", "vol1", "vol2"])
    df = pd.read_csv(path_save + f"Data/{id_company}/docs/link.csv")
    for quy in ["Q1", "Q2", "Q3", "Q4"]:
        for id in df.index:
            year = df[f"Year"][id]
            df_volume.loc[(len(df_volume))] = [f"{year}_{quy}"] + get_data_from_pdf(
                id_company, year, quy, path_save
            )
    if save_file:
        df_volume.to_csv(path_save + f"Data/{id_company}/docs/volume.csv", index=False)
    if return_df:
        return df_volume


def convert_table(df):
    df.loc[-1] = df.columns
    df = df.sort_index()
    df.columns = np.arange(len(df.columns))
    return df.reset_index(drop=True)


def find_row(df, text):
    list_id = np.where((df[0].str.find(text) > 0) == True)[0]
    if len(list_id) == 0:
        return None
    else:
        return list_id[0]


def get_vol_table_tabula(file_path):
    if "https" in file_path:
        tables = tabula.read_pdf(
            file_path, pages="all", multiple_tables=True, silent=True, stream=True
        )
    else:
        tables = tabula.read_pdf(
            file_path, pages="all", multiple_tables=True, silent=True
        )
    for table in range(len(tables)):
        df = pd.DataFrame(tables[table])
        df = convert_table(df)
        row_id = find_row(df, "期末発行済株式数(自己株式を含む)")
        if row_id is not None and len(df.columns) < 10 and len(df[0][0]) < 100:
            return df
    return None


def cut_vol_table(tables):
    for i in range(len(tables)):
        df = tables[i].df
        df_find_key = df[0].str.find("期末発行済株式数（自己株式を含む）")
        for i in df_find_key.index:
            if df_find_key[i] >= 0:
                id_have_key = i
                df = df.iloc[id_have_key:, :].reset_index(drop=True)
                return df


def convert_table_mix_data(df):
    df_add = df[3].str.split(" ", expand=True)
    df_add2 = df[4].str.split(" ", expand=True)
    for i in df.index:
        if df[2][i] == "":
            df[2][i] = df_add[0][i]
            df[3][i] = df_add[1][i]
        if df[5][i] == "":
            df[5][i] = df_add2[1][i]
            df[4][i] = df_add2[0][i]
    return df


def drop_empty_col(df):
    for col in df.columns:
        if (df[col] == "").all():
            df = df.drop(columns=col)
    df.columns = np.arange(len(df.columns))
    return df


def get_vol_table_camelot(file_path):
    tables = camelot.read_pdf(
        file_path,
        pages="all",
        multiple_tables=True,
        flavor="stream",
        suppress_stdout=True,
    )
    df = cut_vol_table(tables)
    # print(df)
    df = convert_table_mix_data(df)
    df = drop_empty_col(df)
    return df


def get_vol_table(file_path="tests/Data/1301/PDF/2022_Q1_決算短信(2022_8_5).pdf"):
    df = get_vol_table_tabula(file_path)
    if df is None:
        df = get_vol_table_camelot(file_path)
    return [
        int(df[2][0].replace(" 株", "").replace(",", "")),
        int(df[2][1].replace(" 株", "").replace(",", "")),
    ]