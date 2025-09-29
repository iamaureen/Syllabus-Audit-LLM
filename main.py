#https://github.com/ASU/aiml-ssmdv-student-support-ml-data-visualization/tree/main/base-ASUllm-documentation



from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_PROVIDERS_URL, TEST_LLMs_REST_API_URL
from ASUllmAPI import query_model_info_api, model_provider_mapper, model_list
from ASUllmAPI import ModelConfig, query_llm, batch_query_llm
from input_processing import read_single_pdf_file


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

    # define the model
    model = ModelConfig(name="gpt4_1", #llama3_2-90b
                        provider="openai", #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    # read input

    # Create a PdfReader object by providing the path to your PDF file
    data = read_single_pdf_file("Data/Copy of CEL 100 Tan Spring 2025 18207.pdf")

    llm_prompt = f"""
    You are an AI agent assisting faculty with auditing syllabus documents.
    For each document that you read, you must:
    
    1. Extract Course Code & Course Title:
       - Parse the document title and separate the course code and course name.
       - Example: If the title is "CEL 100 Great Ideas Politics & Ethics":
           - Course Code: "CEL 100"
           - Course Name: "Great Ideas Politics & Ethics".
    
    2. Extract Lead Instructor Name:
       - Identify the main or lead instructor’s name in the document.
    
    3. Extract Gold Statement & Learning Outcomes Sections:
       - Identify and extract all sections labeled "Gold Statement" and "Learning Outcomes".
       - If such sections are not present, mark them as "NA".
    
    4. Return Output as JSON:
       - Do NOT produce an Excel file.
       - Return results as JSON with the following fields:
           - "file_name": Name of the uploaded file.
           - "full_title": Full course title as written in the document.
           - "course_code": Extracted course code (or "NA" if not found).
           - "course_name": Extracted course name (or "NA" if not found).
           - "instructor_name": Extracted instructor name (or "NA" if not found).
           - "gold_statement": "yes" if a Gold Statement section exists, otherwise "no".
           - "learning_outcome": "yes" if a Learning Outcomes section exists, otherwise "no".
    
    Strictly follow JSON format for output. For example:
    {{
      "file_name": "CEL_100_Syllabus.pdf",
      "full_title": "CEL 100 Great Ideas Politics & Ethics",
      "course_code": "CEL 100",
      "course_name": "Great Ideas Politics & Ethics",
      "instructor_name": "Dr. Jane Smith",
      "gold_statement": "yes",
      "learning_outcome": "no"
    }}

    Do not include any additional commentary—just the JSON output.

    Extracted document content:
    \"\"\"
    {data}
    \"\"\"
    """

    execute_single_query(llm_prompt)

