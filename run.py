from save_pdf import save_pdf
from get_volume import get_volume
import time

a = time.process_time()
id_company = 1333

print('Start', id_company)
save_pdf(id_company)
print('Save pdf done')
get_volume(id_company)
print('Get volume done')
b = time.process_time()
print(int(b-a))