skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections
    input: Path to .txt policy file (string)
    output: Dictionary mapping section numbers to section content (e.g., {"2.3": "Employees must submit...", "5.2": "LWP requires approval from the Department Head and the HR Director..."})
    error_handling: Raise FileNotFoundError if file not found, ValueError if extension not .txt

  - name: summarize_policy
    description: Takes structured policy sections, produces compliant summary with clause references
    input: Dictionary of section_number -> content from retrieve_policy
    output: Text summary with each obligation mapped to its source clause number
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it