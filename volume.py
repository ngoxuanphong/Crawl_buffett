from src.readPdf import ReadPdf

read_pdf = ReadPdf(path_all_com="docs\May_anhNA.csv",
                   path_save='')
read_pdf.getAllCom(reverse=False, 
                     bool_get_volume=True, 
                     bool_get_dividend=False, 
                     bool_get_table=False)