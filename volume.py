from src.readPdf import ReadPdf

read_pdf = ReadPdf(path_all_com="docs\May_anhNA.csv",
                   path_save='')
read_pdf.getAllCom(reverse=True, 
                     bool_get_volume=True, 
                     bool_get_dividend=False, 
                     bool_get_table=False)
# from src.volume import GetVolume
# GetVolume(path_save='').getVolume(id_company=1381)