#https://github.com/ASU/aiml-ssmdv-student-support-ml-data-visualization/tree/main/base-ASUllm-documentation

from pypdf import PdfReader

from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_PROVIDERS_URL, TEST_LLMs_REST_API_URL
from ASUllmAPI import query_model_info_api, model_provider_mapper, model_list
from ASUllmAPI import ModelConfig, query_llm, batch_query_llm


def execute_single_query(query):
    # Use query_llm module to query ASU GPT.
    llm_response = query_llm(model=model,
                             query=query,
                             # number of retries when API call is NOT successful
                             num_retry=3,
                             # number of seconds to sleep when API call successful
                             success_sleep=0.0,
                             # number of seconds to sleep when API call is NOT successful
                             fail_sleep=1.0)
    print(llm_response['response'])


if __name__ == '__main__':

    #define the model
    model = ModelConfig(name="gpt4_1", #llama3_2-90b
                        provider="openai", #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    # Create a PdfReader object by providing the path to your PDF file
    reader = PdfReader("Data/Copy of CEL 100 Tan Spring 2025 18207.pdf")

    # Get the total number of pages in the PDF
    num_pages = len(reader.pages)
    print(f"Number of pages: {num_pages}")

    # Access a specific page (e.g., the first page, index 0)
    # page = reader.pages[0]
    # Extract text from the page
    # text = page.extract_text()
    # print(f"Text from the first page:\n{text}")

    # Extract text from all pages
    all_text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            all_text += f"\n\n--- Page {i + 1} ---\n{page_text}"

    # Print the complete extracted text
    # print(all_text)

    llm_prompt = f"""
    You are an assistant helping a faculty member audit a syllabus document. The following text was extracted from a syllabus. Your task is to:

    1. Scan the content and identify if the syllabus includes:
       - a course title for example CEl, ABS
       - a "Gold Statement" (or similar mission/vision/value statement),
       - a "Learning Outcomes" section (or similar language such as "Objectives", "Goals", or "Expected Outcomes").

    2. Return your findings in valid JSON format with the following structure:

    {{
      "file_name": "Copy of CEL 100 Tan Spring 2025 18207.pdf",
      "course_title": "Extracted course title here, or empty string if not found"
      "gold_statement_present": true or false,
      "learning_outcomes_present": true or false,
      "gold_statement_text": "Extracted text here, or empty string if not found",
      "learning_outcomes_text": "Extracted text here, or empty string if not found"
    }}

    Do not include any additional commentary—just the JSON output.

    Extracted document content:
    \"\"\"
    {all_text}
    \"\"\"
    """

    execute_single_query(llm_prompt)

