"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "hole", "pot hole"],
    "Flooding": ["flood", "flooding", "water", "logged", "standing water"],
    "Streetlight": ["streetlight", "street light", "light out", "lamp", "pole light"],
    "Waste": ["waste", "garbage", "trash", "litter", "rubbish", "dustbin", "bin"],
    "Noise": ["noise", "loud", "music", "party", "drilling", "construction noise"],
    "Road Damage": ["road damage", "road", "crack", "broken road", "surface"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "building"],
    "Heat Hazard": ["heat", "hot", "temperature", "heatwave", "sun"],
    "Drain Blockage": ["drain", "drainage", "blocked", "clog", "sewer"]
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()
    matched_category = None
    match_reason = ""

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                matched_category = category
                match_reason = keyword
                break
        if matched_category:
            break

    if not matched_category:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Standard",
            "reason": "Unable to determine category from description",
            "flag": "NEEDS_REVIEW"
        }

    priority = "Standard"
    for keyword in URGENT_KEYWORDS:
        if keyword in description_lower:
            priority = "Urgent"
            match_reason = keyword
            break

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": matched_category,
        "priority": priority,
        "reason": f"Found keyword: {match_reason}",
        "flag": ""
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []
    for row in rows:
        try:
            classified = classify_complaint(row)
            results.append(classified)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": f"Error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")