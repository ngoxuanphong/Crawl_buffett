from save_pdf import GetPDF

get_pdf = GetPDF(
                path_all_com="docs/List_company_23052023 - Listing.csv",
                path_save="Data",
                time_sleep=1, 
                browser_name='PC')
get_pdf.save_pdf(id_company=9980)
