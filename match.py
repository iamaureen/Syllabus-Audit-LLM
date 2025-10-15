import os
import sys
import pandas as pd
import json
import glob

from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig, query_llm
from load_gold_statements_csv import load_gold_statements_csv


def find_designation_file():
    """
    Automatically detect which designation file to use:
    - Look for files ending with "_designation.xlsx" in Output directory
    - Return the most recent one if multiple exist
    """
    output_dir = "Output"
    if not os.path.exists(output_dir):
        return None
    
    # Look for designation files
    designation_files = glob.glob(os.path.join(output_dir, "*_designation.xlsx"))
    
    if designation_files:
        # If multiple files, use the most recent one
        most_recent = max(designation_files, key=os.path.getmtime)
        return most_recent
    
    return None


def match_gold_statements_with_llm(model, gold_destination, syllabus_statement, expected_statement):
    """
    Use LLM as judge to determine if syllabus statement matches the expected statement.
    Returns: "matched", "not matched", or "not present" (when syllabus statement is missing).
    """
    # If syllabus statement missing/empty → not present
    if syllabus_statement == 'NA' or not str(syllabus_statement).strip():
        return "not present"

    # If expected statement unavailable, treat as not matched (cannot verify)
    if expected_statement is None or expected_statement == 'NA' or not str(expected_statement).strip():
        return "not matched"
    
    prompt = f"""
You are an impartial evaluator for academic course statements. Determine if a syllabus Gold Statement matches the required criteria for a specific General Studies Gold designation area.

Instructions:
- Carefully compare the provided syllabus Gold Statement against the official expected statement.
- Consider exact text matching, ignore bullet points.
- Answer strictly in JSON with keys: "match" ("yes" or "no") and "reason" (concise justification).

Gold Designation Area: {gold_destination}

Official Expected Statement:
{expected_statement}

Syllabus Gold Statement:
{syllabus_statement}

JSON only:
{{"match":"yes|no","reason":"..."}}
"""

    try:
        resp = query_llm(model=model, query=prompt, num_retry=3, success_sleep=0.0, fail_sleep=1.0)
        response_text = resp.get('response', '')
        
        # Parse JSON response
        try:
            # Try to extract JSON from response if it's wrapped in other text
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_text = response_text[start:end + 1]
                result = json.loads(json_text)
                return "matched" if result.get('match') == 'yes' else "not matched"
            else:
                return "not matched"
        except json.JSONDecodeError:
            return "not matched"
            
    except Exception as e:
        print(f"  LLM error: {e}")
        return "not matched"


def process_gold_matching():
    """
    Main function to process gold statement matching.
    Automatically finds designation file and creates matched file.
    """
    # Automatically detect designation file
    designation_path = find_designation_file()
    if not designation_path:
        print("Error: No designation file found. Run main.py and map_course_designation.py first.")
        return False

    print(f"Found designation file: {designation_path}")

    # Paths
    csv_path = os.path.join("Map", "gold_statements.csv")

    try:
        df = pd.read_excel(designation_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    # Check required columns
    required_columns = ['course_code', 'gold_designation', 'gold_statement']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns in {designation_path}: {missing_columns}")
        return False

    # Load gold statements dictionary
    gold_statements_dict = load_gold_statements_csv(csv_path)
    if not gold_statements_dict:
        print("Warning: gold_statements_dict is empty; matching will be skipped.")
        return False

    # Initialize model for LLM-as-judge
    model = ModelConfig(
        name="gpt4_1",
        provider="openai",
        access_token=TEST_LLMs_API_ACCESS_TOKEN,
        api_url=TEST_LLMs_REST_API_URL
    )

    # Store match results for each row
    match_results = []

    # For each entry, match gold statements using LLM
    for idx, row in df.iterrows():
        course_code = str(row.get('course_code', '')).strip()
        gold_designation = str(row.get('gold_designation', '')).strip()
        syllabus_statement = str(row.get('gold_statement', '')).strip()
        
        print(f"{course_code} -> {gold_designation}")
        
        # Get expected statement from CSV
        expected_statement = gold_statements_dict.get(gold_designation)
        
        # Match gold statements using LLM
        match_result = match_gold_statements_with_llm(model, gold_designation, syllabus_statement, expected_statement)
        match_results.append(match_result)
        print(f"  Match result: {match_result}")

    # Add match results as a new column
    df['match_result'] = match_results
    
    # Create output filename with "_matched" extension
    base_name = os.path.splitext(designation_path)[0]
    output_path = f"{base_name}_matched.xlsx"
    
    # Save updated results file
    try:
        df.to_excel(output_path, index=False, na_rep='NA')
        print(f"\nCreated {output_path} with match_result column")
        return True
    except Exception as e:
        print(f"Error saving updated Excel file: {e}")
        return False


def main():
    """Legacy main function for backward compatibility."""
    process_gold_matching()


if __name__ == "__main__":
    main()

