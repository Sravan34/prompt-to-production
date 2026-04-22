skills:
  - name: load_dataset
    description: Reads CSV, validates columns, reports null count and which rows before returning
    input: Path to CSV file (string)
    output: Dictionary with data, column names, null rows info (ward, period, category, notes)
    error_handling: Raise ValueError if required columns missing, report all null rows with reason

  - name: compute_growth
    description: Takes ward + category + growth_type, returns per-period table with formula shown
    input: filtered data (from load_dataset), ward, category, growth_type (MoM or YoY)
    output: Table with period, actual_spend, growth_pct, formula columns
    error_handling: If growth_type not specified, refuse and ask. Flag null actual_spend without computing - output NULL with reason