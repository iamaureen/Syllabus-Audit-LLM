"""
Main entry point for the Syllabus Audit application.
Supports processing single PDF files or entire folders.
"""

from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_PROVIDERS_URL, TEST_LLMs_REST_API_URL
import json
import pandas as pd
import os
from prompt_builder import build_syllabus_audit_prompt
from ASUllmAPI import query_model_info_api, model_provider_mapper, model_list
from ASUllmAPI import ModelConfig, query_llm, batch_query_llm
from input_processing import read_single_pdf_file, read_pdfs_from_folder
from map_course_designation import process_course_designation
from match import process_gold_matching


def execute_single_query(query, model):
    """Execute a single LLM query."""
    llm_response = query_llm(model=model,
                             query=query,
                             num_retry=3,
                             success_sleep=0.0,
                             fail_sleep=1.0)
    return llm_response.get('response')


def parse_llm_response(response_text):
    """Parse LLM response and extract JSON."""
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
    return parsed


def process_single_pdf(pdf_path, model, output_file=None):
    """
    Process a single PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        model: LLM model configuration
        output_file (str): Output Excel file path (optional, defaults to input filename)
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return

    print(f"Processing single PDF: {pdf_path}")

    # Read PDF content
    data = read_single_pdf_file(pdf_path)
    file_name = os.path.basename(pdf_path)

    # Set default output file based on input filename
    if output_file is None:
        # Remove .pdf extension and add .xlsx
        base_name = os.path.splitext(file_name)[0]
        output_file = f"Output/{base_name}.xlsx"

    # Build prompt and execute query
    llm_prompt = build_syllabus_audit_prompt(filename=file_name, data=data)
    response_text = execute_single_query(llm_prompt, model)

    # Parse response
    parsed = parse_llm_response(response_text)

    # Save result
    df = pd.DataFrame([parsed])
    df.to_excel(output_file, index=False)
    print(f"Single PDF result saved to {output_file}")
    
    # Automatically add gold designations
    print("Adding gold designations...")
    process_course_designation()
    
    # Automatically perform gold statement matching
    print("Performing gold statement matching...")
    process_gold_matching()

    return parsed


def process_folder(folder_path, model, output_file="Output/all_results.xlsx", max_files=None):
    """
    Process all PDF files in a folder.
    
    Args:
        folder_path (str): Path to folder containing PDF files
        model: LLM model configuration
        output_file (str): Output Excel file path
        max_files (int): Maximum number of files to process (None for all)
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return

    print(f"Processing folder: {folder_path}")

    # Read all PDFs from folder
    pdf_data = read_pdfs_from_folder(folder_path)

    if not pdf_data:
        print("No PDF files found in the folder")
        return

    results = []

    for file_name, data in pdf_data.items():
        print(f"Processing: {file_name}")

        # Build prompt and execute query
        llm_prompt = build_syllabus_audit_prompt(filename=file_name, data=data)
        response_text = execute_single_query(llm_prompt, model)

        # Parse response
        parsed = parse_llm_response(response_text)
        results.append(parsed)

    # Save results
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"Folder processing complete. Results saved to {output_file}")
    print(f"Processed {len(results)} files")
    
    # Automatically add gold designations
    print("Adding gold designations...")
    process_course_designation()
    
    # Automatically perform gold statement matching
    print("Performing gold statement matching...")
    process_gold_matching()

    return results


def main():
    """Main function - example usage of the processing functions."""
    # Initialize model
    model = ModelConfig(name="gpt4_1",
                        provider="openai",
                        access_token=TEST_LLMs_API_ACCESS_TOKEN,
                        api_url=TEST_LLMs_REST_API_URL)

    # Example 1: Process a single PDF
    # process_single_pdf("Data/Copy of CIS 105 - McCarthy - C - 23330-10466-10467.pdf", model)

    # Example 2: Process all PDFs in a folder
    process_folder("Data/", model)


if __name__ == '__main__':
    main()
