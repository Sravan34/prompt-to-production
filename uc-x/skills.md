# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number
    input: None — reads policy files from data/policy-documents/
    output: Dictionary indexed by document name and section number
    error_handling: Returns error if policy files are missing or cannot be read

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template
    input: Question string
    output: Single-source answer with document name and section number, or refusal template
    error_handling: Returns refusal template when question is not covered in available policy documents