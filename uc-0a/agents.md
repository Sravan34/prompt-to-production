# agents.md — UC-0A Complaint Classifier

role: >
  Agent that classifies citizen complaints by category and priority for municipal service requests.

intent: >
  Output a CSV with columns: category, priority, reason, flag. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other. Priority must be Urgent, Standard, or Low. Reason must cite specific words from the description. Flag must be NEEDS_REVIEW or blank.

context: >
  Input file: ../data/city-test-files/test_[city].csv with description column. Output file: results_[city].csv. Use only the description field to classify. Do not use any external information or assumptions.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other"
  - "Priority must be Urgent if description contains any of: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse; otherwise Standard or Low"
  - "Every output row must include a reason field citing specific words from the description"
  - "If category cannot be determined from description alone, output category: Other and flag: NEEDS_REVIEW"