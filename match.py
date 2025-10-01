import os
import sys
import pandas as pd
import json

from config import TEST_LLMs_API_ACCESS_TOKEN, TEST_LLMs_REST_API_URL
from ASUllmAPI import ModelConfig, query_llm
from load_gold_statements_csv import load_gold_statements_csv


def match_gold_statements_with_llm(model, gold_destination, syllabus_statement, expected_statement):
    """
    Use LLM as judge to determine if syllabus statement matches the expected statement.
    Returns: "match", "NA", or "did not match"
    """
    # Check if syllabus statement is empty or NA
    if syllabus_statement == 'NA' or not syllabus_statement.strip():
        return "NA"
    
    # Check if expected statement is not available
    if expected_statement is None or expected_statement == 'NA' or not expected_statement.strip():
        return "NA"
    
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
                return "match" if result.get('match') == 'yes' else "did not match"
            else:
                return "did not match"
        except json.JSONDecodeError:
            return "did not match"
            
    except Exception as e:
        print(f"  LLM error: {e}")
        return "did not match"


def main():
    # Paths
    results_path = os.path.join("Output", "results.xlsx")
    csv_path = os.path.join("Map", "gold_statements.csv")

    if not os.path.exists(results_path):
        print(f"Error: Could not find Excel file at {results_path}. Run main.py first.")
        sys.exit(1)

    try:
        df = pd.read_excel(results_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    # Check required columns
    required_columns = ['course_code', 'gold_destination', 'gold_statement']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Error: Missing columns in results.xlsx: {missing_columns}")
        sys.exit(1)

    # Load gold statements dictionary
    gold_statements_dict = load_gold_statements_csv(csv_path)
    if not gold_statements_dict:
        print("Warning: gold_statements_dict is empty; matching will be skipped.")
        sys.exit(1)

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
        gold_destination = str(row.get('gold_destination', '')).strip()
        syllabus_statement = str(row.get('gold_statement', '')).strip()
        
        print(f"{course_code} -> {gold_destination}")
        
        # Get expected statement from CSV
        expected_statement = gold_statements_dict.get(gold_destination)
        
        # Match gold statements using LLM
        match_result = match_gold_statements_with_llm(model, gold_destination, syllabus_statement, expected_statement)
        match_results.append(match_result)
        print(f"  Match result: {match_result}")

    # Add match results as a new column
    df['match_result'] = match_results
    
    # Save updated results.xlsx
    try:
        df.to_excel(results_path, index=False)
        print(f"\nUpdated {results_path} with match_result column")
    except Exception as e:
        print(f"Error saving updated Excel file: {e}")


if __name__ == "__main__":
    main()

