import io
import fitz  # PyMuPDF
from pypdf import PdfWriter, PdfReader

def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
    """Merges multiple pdfs (in order) into a single PDF."""
    merger = PdfWriter()
    for pdf_bytes in pdf_bytes_list:
        merger.append(io.BytesIO(pdf_bytes))
    output = io.BytesIO()
    merger.write(output)
    return output.getvalue()

def split_pdf(pdf_bytes: bytes, pages: list[int]) -> bytes:
    """
    Extracts specific pages from a PDF.
    Pages are 1-indexed.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for page_num in pages:
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def remove_pages(pdf_bytes: bytes, pages_to_remove: list[int]) -> bytes:
    """
    Removes specific pages from a PDF.
    Pages are 1-indexed.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if (i + 1) not in pages_to_remove:
            writer.add_page(page)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def compress_pdf(pdf_bytes: bytes) -> bytes:
    """
    Compresses a PDF using PyMuPDF's garbage collection and deflation.
    """
    doc = fitz.open("pdf", pdf_bytes)
    output = doc.tobytes(
        garbage=4,
        clean=True,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True
    )
    return output
