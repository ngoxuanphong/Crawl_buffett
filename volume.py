from src.readPdf import ReadPdf

read_pdf = ReadPdf(path_all_com="docs/List_company_23052023 - Listing.csv",
                   path_save='')
read_pdf.getAllCom(reverse=True, 
                     bool_get_volume=True, 
                     bool_get_dividend=False, 
                     bool_get_table=False)