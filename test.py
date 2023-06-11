# from run import get_company

# get_company(id_company=5486)
# get_company(id_company=1333)
# get_company(id_company=1301)
# get_company(id_company=3333)
# from volume.get_volume import get_volume, get_data_from_pdf
# id = 1301
# print(id)
# df = get_volume(id, path_save = 'tests/', return_df = True, save_file = False)
# print(df)

# from volume.ocr_volume import ocr_pdf
# ocr_pdf('tests/Data/1301/PDF/2013_Q4_決算短信(2014_5_9).pdf')
# from volume.get_volume import convert_pdf_to_text, find_row 
# ocr_pdf('tests/Data/1301/PDF/2017_Q4_決算短信(2018_5_10).pdf')
# text = convert_pdf_to_text('tests/ocr.pdf').replace(' ', '').replace('.', ',')
# # text = convert_pdf_to_text('tests/Data/1301/PDF/2021_Q4_決算短信(2022_5_13).pdf').replace(' ', '').replace('.', ',')
# print(text)
# lst_data_of_time = find_row(text)
# print(lst_data_of_time)

from dividend.dividend import get_dividend

df = get_dividend(id_company=1301, path_save = 'tests/', return_df = True, save_file = False)
print(df)