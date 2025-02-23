import os
from io import BytesIO
from PIL import Image
import fitz


def generate_thumbnail(file_path):
    file_ext = os.path.splitext(file_path)[1]
    if file_ext.lower() == '.pdf':
        img_bytes = pdf_to_image(file_path)
    else: 
        img = Image.open(file_path)
        img.thumbnail((500, 500))
        thumb_io = BytesIO()
        img.save(thumb_io, img.format)
        img_bytes = thumb_io.getvalue()
    return img_bytes



def pdf_to_image(pdf_file):
    with fitz.open(pdf_file) as doc:
        page = doc.load_page(0)
        pixmap = page.get_pixmap()
        img_bytes = pixmap.tobytes()
    return img_bytes