import pandas as pd
import os


def process_gold_courses():
    """
    Read the CSV file from Map folder and create a dictionary where:
    - Key: Subject + " " + Nbr (e.g., "ABS 130")
    - Value: Gold Designation
    Once the dictionary is created, read results.xlsx and add gold_destination column
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

        # Read results.xlsx and add gold_destination column
        results_path = "Output/results.xlsx"
        if os.path.exists(results_path):
            try:
                results_df = pd.read_excel(results_path)
                
                # Add gold_destination column
                gold_destinations = []
                for _, row in results_df.iterrows():
                    course_code = str(row.get('course_code', '')).strip()
                    gold_destination = course_gold_dict.get(course_code, 'NA')
                    gold_destinations.append(gold_destination)
                
                results_df['gold_destination'] = gold_destinations
                
                # Save updated results.xlsx
                results_df.to_excel(results_path, index=False)
                print(f"Updated results.xlsx with gold_destination column")
                
            except Exception as e:
                print(f"Error updating results.xlsx: {e}")
        else:
            print(f"Warning: {results_path} not found. Skipping Excel update.")

        return course_gold_dict

    except FileNotFoundError:
        print(f"Error: Could not find the file {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error processing the file: {e}")
        return None


if __name__ == "__main__":
    course_dict = process_gold_courses()