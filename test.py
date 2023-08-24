from src.morningstar import Morningstar

ms = Morningstar(path_download = fr'A:\Phong\Crawl_buffett\Financial',
                 email = 'quynhtranga1k2000@gmail.com',
                 password = 'Trang0987145288')

ms.run(path_symbol = 'docs\ListCom_Germany.xlsx')