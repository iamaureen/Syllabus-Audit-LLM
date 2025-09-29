import pandas as pd


def process_gold_courses():
    """
    Read the CSV file from Map folder and create a dictionary where:
    - Key: Subject + " " + Nbr (e.g., "ABS 130")
    - Value: Gold Designation
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

        return course_gold_dict

    except FileNotFoundError:
        print(f"Error: Could not find the file {csv_file_path}")
        return None
    except Exception as e:
        print(f"Error processing the file: {e}")
        return None


if __name__ == "__main__":
    course_dict = process_gold_courses()