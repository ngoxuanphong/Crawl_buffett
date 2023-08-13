import PyPDF2
import ocrmypdf

import threading
import time, os

# Hàm kiểm tra thời gian và ngắt hàm nếu cần
def timeout_function(func, timeout):
    result = None
    exception = None

    def target():
        nonlocal result, exception
        try:
            result = func()
        except Exception as e:
            exception = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Nếu thread vẫn còn sống sau thời gian quy định, ngắt nó
        raise TimeoutError("Hàm đã chạy quá thời gian quy định")
    elif exception:
        # Nếu có exception trong quá trình chạy hàm, ném lại exception
        raise exception
    else:
        return result
    

def ocrPDF_(input_file, output_file = None):
    if os.path.getsize(input_file) > 600000:
        print("File too large, skip OCR", os.path.getsize(input_file))
        return output_file
    if output_file == None:
        output_file = input_file.replace(".pdf", "_ocr.pdf")
    ocrmypdf.ocr(
        input_file,
        output_file,
        language="eng+jpn",
        force_ocr=True,
        output_type="pdf",
        optimize=0,
        progress_bar=False,
        # skip_big = True,
        max_image_mpixels=500,
    )
    return output_file

def ocrPDF(input_file, output_file = None):
    timeout_function(ocrPDF_(input_file, output_file), 20)


def convertPDFToText(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            t = page.extract_text()
            text += t

    return text
