from src.save_pdf import GetPDF

bf = GetPDF(
    path_all_com="docs/List_company_23052023 - Listing.csv",
    path_save="Data",
    time_sleep=35,
    browser_name="Chrome",
    # tor_path=r"A:\Tor Browser",
    # headless=True
)
bf.checklist_download_pdf()
