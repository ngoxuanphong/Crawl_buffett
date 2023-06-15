from save_pdf import GetPDF

bf = GetPDF(
            path_all_com="docs/List_company_23052023 - Listing.csv",
            path_save="Data",
            time_sleep=1,
            browser_name="PC",
            tor_path=r"A:\Tor Browser",
        )
bf.save_pdf(id_company=9980)
