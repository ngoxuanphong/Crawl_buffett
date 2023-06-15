from save_pdf import GetPDF

bf = GetPDF(
            path_all_com="docs/List_company_23052023 - Listing.csv",
            path_save="Data",
            time_sleep=2,
            browser_name="PC",
            tor_path=r"A:\Tor Browser",
            # headless=True
        )
bf.get_all_com(reverse=True)