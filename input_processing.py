from pypdf import PdfReader
import os


def read_single_pdf_file(filePath):
    # Create a PdfReader object by providing the path to your PDF file
    reader = PdfReader(filePath)

    # Get the total number of pages in the PDF
    # num_pages = len(reader.pages)
    # print(f"Number of pages: {num_pages}")

    # Access a specific page (e.g., the first page, index 0) and Extract text from the it
    # page = reader.pages[0]
    # text = page.extract_text()
    # print(f"Text from the first page:\n{text}")

    # Extract text from all pages
    all_text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            all_text += f"\n\n--- Page {i + 1} ---\n{page_text}"

    return all_text


def read_pdfs_from_folder(folder_path):
    """
    Reads all PDF files in a folder and stores their extracted text in a dictionary.
    Key = PDF filename, Value = extracted text.
    """
    pdf_texts = {}

    for filename in os.listdir(folder_path):
        print(filename)
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            print(f"Reading: {filename}")
            pdf_texts[filename] = read_single_pdf_file(file_path)

    return pdf_texts
