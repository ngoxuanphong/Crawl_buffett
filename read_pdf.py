from src.readPdf import ReadPdf

read_pdf = ReadPdf(path_all_com="docs/List_company_23052023 - Listing.csv",
                   path_save='Data')
read_pdf.get_all_com(reverse=True)                                                                                                  