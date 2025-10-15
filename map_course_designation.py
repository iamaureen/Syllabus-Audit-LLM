import pandas as pd
import os
import glob


def find_result_file():
    """
    Automatically detect which result file to use:
    - If single PDF result exists (Output/*.xlsx but not all_results.xlsx), use the single file
    - If all_results.xlsx exists, use that
    - Return None if no result files found
    """
    output_dir = "Output"
    if not os.path.exists(output_dir):
        return None
    
    # Look for all_results.xlsx first (folder processing)
    all_results_path = os.path.join(output_dir, "all_results.xlsx")
    if os.path.exists(all_results_path):
        return all_results_path
    
    # Look for single PDF result files (any .xlsx except all_results.xlsx)
    single_files = glob.glob(os.path.join(output_dir, "*.xlsx"))
    single_files = [f for f in single_files if not f.endswith("all_results.xlsx")]
    
    if single_files:
        # If multiple single files, use the most recent one
        most_recent = max(single_files, key=os.path.getmtime)
        return most_recent
    
    return None


def process_course_designation():
    """
    Read the CSV file from Map folder and create a dictionary where:
    - Key: Subject + " " + Nbr (e.g., "ABS 130")
    - Value: Gold Designation
    Once the dictionary is created, read the appropriate results file and add gold_designation column
    """
    # Read the CSV file
    csv_file_path = "Map/ASU Courses and Topics Approved for General Studies - General Studies Gold.csv"

    try:
        df = pd.read_csv(csv_file_path)

        # Create dictionary by combining Subject and Nbr columns
        course_gold_dict = {}

        for index, row in df.iterrows():
            subject = str(row['Subject']).strip()
            nbr = str(row['Nbr']).strip()
            gold_designation = str(row['Gold Designation']).strip()
            # Remove abbreviation enclosed in parentheses at the end
            if gold_designation.endswith(')'):
                # Find the last opening parenthesis
                last_open_paren = gold_designation.rfind('(')
                if last_open_paren != -1:
                    gold_designation = gold_designation[:last_open_paren].strip()

            # Combine Subject and Nbr with a space
            course_key = f"{subject} {nbr}"
            course_gold_dict[course_key] = gold_designation

        # Print first 5 entries
        print("First 5 entries of the course dictionary:")
        print("-" * 50)

        count = 0
        for key, value in course_gold_dict.items():
            if count >= 5:
                break
            print(f"'{key}': '{value}'")
            count += 1

        print(f"\nTotal number of courses: {len(course_gold_dict)}")

        # Automatically detect result file
        results_path = find_result_file()
        if results_path:
            print(f"Found result file: {results_path}")
            try:
                results_df = pd.read_excel(results_path)
                
                # Add gold_designation column
                gold_designations = []
                for _, row in results_df.iterrows():
                    course_code = str(row.get('course_code', '')).strip()
                    if course_code == 'NA' or not course_code:
                        gold_designations.append('NA')
                    else:
                        gold_designation = course_gold_dict.get(course_code, 'NA')
                        gold_designations.append(gold_designation)
                
                results_df['gold_designation'] = gold_designations
                
                # Create output filename with "_designation" extension
                base_name = os.path.splitext(results_path)[0]
                output_path = f"{base_name}_designation.xlsx"
                
                # Save updated results file (preserve all data including NAs)
                results_df.to_excel(output_path, index=False, na_rep='NA')
                print(f"Created {output_path} with gold_designation column")
                
            except Exception as e:
                print(f"Error updating {results_path}: {e}")
        else:
            print("Warning: No result files found in Output/ directory. Skipping Excel update.")

        return course_gold_dict

    except FileNotFoundError:
        print(f"Error: Could not find the file {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error processing the file: {e}")
        return None


if __name__ == "__main__":
    course_dict = process_course_designation()