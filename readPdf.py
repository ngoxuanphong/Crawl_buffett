from src.readPdf import ReadPdf

read_pdf = ReadPdf(path_all_com="docs\may_cty.csv",
                   path_save='',
                   PATH_DRIVER="I:/My Drive/6_2023/DoneJapan")

read_pdf.getAllCom(reverse=True, 
                     bool_get_volume=True, 
                     bool_get_dividend=True, 
                     bool_get_table=True, 
                     list_symbol=[])

read_pdf.moveToDrive(move_volume=True,
                     move_dividend=True,
                     move_financial=False,
                        list_symbol=[])
