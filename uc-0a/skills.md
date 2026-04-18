skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and flag
    input: Object with description field (string)
    output: Object with category, priority, reason, and flag fields
    error_handling: If category cannot be determined from description, output category: Other and flag: NEEDS_REVIEW

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV
    input: CSV file path with description column
    output: CSV file with category, priority, reason, and flag columns
    error_handling: If any row is ambiguous, flag it as NEEDS_REVIEW