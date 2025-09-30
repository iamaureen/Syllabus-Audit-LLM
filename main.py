#https://github.com/ASU/aiml-ssmdv-student-support-ml-data-visualization/tree/main/base-ASUllm-documentation


from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_PROVIDERS_URL, TEST_LLMs_REST_API_URL
import json
import pandas as pd
from prompt_builder import build_syllabus_audit_prompt
from ASUllmAPI import query_model_info_api, model_provider_mapper, model_list
from ASUllmAPI import ModelConfig, query_llm, batch_query_llm
from input_processing import read_single_pdf_file, read_pdfs_from_folder


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
    return llm_response.get('response')


if __name__ == '__main__':
    # define the model
    model = ModelConfig(name="gpt4_1",  #llama3_2-90b
                        provider="openai",  #aws
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)
    # read input

    # Create a PdfReader object by providing the path to your PDF file
    data = read_single_pdf_file("Data/Copy of CEL 100 Tan Spring 2025 18207.pdf")

    # read multiple pdf from a folder
    pdf_data = read_pdfs_from_folder("Data/")

    results = []
    for file_name, data in pdf_data.items():
        llm_prompt = build_syllabus_audit_prompt(filename=file_name, data=data)
        response_text = execute_single_query(llm_prompt)

        # Expecting strict JSON per instructions above
        try:
            parsed = json.loads(response_text) if isinstance(response_text, str) else response_text
        except Exception:
            # If the model returned code fences or stray text, try to salvage the JSON substring
            if isinstance(response_text, str):
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    parsed = json.loads(response_text[start:end + 1])
                else:
                    raise
            else:
                raise

        results.append(parsed)

    # Convert results to DataFrame and save as Excel
    df = pd.DataFrame(results)
    df.to_excel("results.xlsx", index=False)
    print("Results saved to results.xlsx")

    # Comment out JSON writing code
    # print(json.dumps(results, indent=2))
    # with open("results.json", "w", encoding="utf-8") as f:
    #     json.dump(results, f, indent=2, ensure_ascii=False)


