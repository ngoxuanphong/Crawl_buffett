import PyPDF2
import ocrmypdf

def ocr_pdf(input_file):
    output_file = input_file.replace('.pdf', '_ocr.pdf')
    ocrmypdf.ocr(input_file, output_file,
                    language= 'eng+jpn',
                    force_ocr = True,
                    output_type='pdf',
                    optimize=0,
                    progress_bar = False,
                    # skip_big = True,
                    max_image_mpixels = 500,
                    )
    return output_file


def convert_pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            t = page.extract_text()
            text += t
    
    return text