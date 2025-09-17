from pypdf import PdfReader


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
