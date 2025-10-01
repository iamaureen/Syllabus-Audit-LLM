"""
Module for loading gold statements from CSV file.
"""
import os
import pandas as pd


def load_gold_statements_csv(csv_path):
    """
    Load gold_statements.csv and create a dictionary mapping gold_designation to statements.
    
    Args:
        csv_path (str): Path to the gold_statements.csv file
        
    Returns:
        dict: Dictionary mapping gold_designation to statements
              Format: { gold_designation: statement }
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV not found at {csv_path}")
        return {}

    try:
        df = pd.read_csv(csv_path)
        gold_dict = {}
        
        for _, row in df.iterrows():
            designation = str(row['gold_designation']).strip()
            statement = str(row['statements']).strip()
            gold_dict[designation] = statement
            
        return gold_dict
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return {}


if __name__ == "__main__":
    # Test the function
    csv_path = "Map/gold_statements.csv"
    gold_dict = load_gold_statements_csv(csv_path)
    
    if gold_dict:
        print("Successfully loaded gold statements:")
        for designation, statement in list(gold_dict.items())[:3]:  # Show first 3
            print(f"  {designation}: {statement[:100]}...")
        print(f"Total entries: {len(gold_dict)}")
    else:
        print("Failed to load gold statements")