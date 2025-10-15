def build_syllabus_audit_prompt(filename, data):
    return f"""
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
   - Identify and extract the full text content of sections labeled "Gold Statement" and "Learning Outcomes".
   - If the sections are not present in the document, mark them as "NA".
   - Include the complete text content of these sections, not just "yes" or "no".

4. Return Output as JSON:
   - Do NOT produce an Excel file.
   - Return results as JSON with the following fields:
       - "file_name": MUST be exactly "{filename}" (use this exact filename, do not extract from document).
       - "full_title": Full course title as written in the document.
       - "course_code": Extracted course code (or "NA" if not found).
       - "course_name": Extracted course name (or "NA" if not found).
       - "instructor_name": Extracted instructor name (or "NA" if not found).
       - "gold_statement": Full text content of the Gold Statement section (or "NA" if not found).
       - "learning_outcome": Full text content of the Learning Outcomes section (or "NA" if not found).

IMPORTANT: The "file_name" field must be exactly "{filename}" - do not change it or extract a different filename from the document content.

Strictly follow JSON format for output. For example:
{{
  "file_name": "{filename}",
  "full_title": "CEL 100 Great Ideas Politics & Ethics",
  "course_code": "CEL 100",
  "course_name": "Great Ideas Politics & Ethics",
  "instructor_name": "Dr. Jane Smith",
  "gold_statement": "This course fulfills the General Studies requirement for Humanities, Arts and Design by exploring fundamental questions about politics and ethics through classic texts.",
  "learning_outcome": "Students will be able to analyze political theories and apply ethical frameworks to contemporary issues."
}}

Do not include any additional commentary—just the JSON output.

Extracted document content:: {data}

"""

