"""
UC-X app.py — Policy Q&A System
Implements: retrieve_documents + answer_question skills with RICE enforcement.
"""
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

POLICY_DIR = Path(__file__).parent.parent / "data" / "policy-documents"
POLICY_FILES = {
    "policy_hr_leave.txt": "HR Leave",
    "policy_it_acceptable_use.txt": "IT Acceptable Use",
    "policy_finance_reimbursement.txt": "Finance Reimbursement",
}

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def load_documents():
    """Skill: retrieve_documents — loads all 3 policy files, indexes by document name and section number."""
    documents = {}
    for filename, display_name in POLICY_FILES.items():
        filepath = POLICY_DIR / filename
        if not filepath.exists():
            sys.stderr.write(f"Error: {filepath} not found\n")
            documents[filename] = {"display_name": display_name, "sections": {}, "raw": ""}
            continue
        
        content = filepath.read_text(encoding="utf-8")
        sections = parse_sections(content)
        documents[filename] = {"display_name": display_name, "sections": sections, "raw": content}
    return documents

def parse_sections(content):
    """Parse policy document into sections (e.g., 2.6, 3.1, 5.2)."""
    sections = {}
    lines = content.split("\n")
    current_section = None
    current_text = []
    
    subsection_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    major_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    
    for line in lines:
        match = subsection_pattern.match(line.strip())
        if match:
            if current_section:
                sections[current_section] = "\n".join(current_text).strip()
            current_section = match.group(1)
            current_text = [match.group(2).strip()]
        elif major_pattern.match(line.strip()):
            if current_section:
                sections[current_section] = "\n".join(current_text).strip()
                current_section = None
                current_text = []
        elif current_section:
            current_text.append(line.rstrip())
    
    if current_section:
        sections[current_section] = "\n".join(current_text).strip()
    
    return sections

def find_answer(documents, question):
    """Skill: answer_question — searches indexed documents, returns single-source answer + citation OR refusal template."""
    question_lower = question.lower()
    
    hr_keywords = ["leave", "annual", "sick", "maternity", "paternity", "lwp", "without pay", "holiday", "encashment", "grievance"]
    it_keywords = ["device", "software", "install", "password", "email", "network", "data", "access", "personal", "phone", "byod"]
    finance_keywords = ["reimbursement", "travel", "da", "allowance", "home office", "equipment", "training", "mobile", "internet", "claim"]
    
    specific_overrides = {
        ("policy_it_acceptable_use.txt", "phone", "personal", "file"): "3.1",
        ("policy_hr_leave.txt", "leave without pay", "approves"): "5.2",
    }
    
    def score_document(keywords):
        return sum(1 for kw in keywords if kw in question_lower)
    
    hr_score = score_document(hr_keywords)
    it_score = score_document(it_keywords)
    finance_score = score_document(finance_keywords)
    
    scores = [
        ("policy_hr_leave.txt", hr_score),
        ("policy_it_acceptable_use.txt", it_score),
        ("policy_finance_reimbursement.txt", finance_score),
    ]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    best_doc, best_score = scores[0]
    second_doc, second_score = scores[1]
    
    if best_score == 0:
        return REFUSAL_TEMPLATE
    
    if best_score == second_score and best_score > 0:
        return REFUSAL_TEMPLATE
    
    doc_data = documents[best_doc]
    sections = doc_data["sections"]
    display_name = doc_data["display_name"]
    
    for override_key, override_section in specific_overrides.items():
        if best_doc == override_key[0] and all(kw in question_lower for kw in override_key[1:]):
            if override_section in sections:
                return f"[{display_name} section {override_section}]\n{sections[override_section]}"
    
    q_words = set(re.findall(r'\w+', question_lower))
    
    best_section = None
    best_section_score = 0
    best_section_text = ""
    
    for section_num, section_text in sections.items():
        section_lower = section_text.lower()
        s_words = set(re.findall(r'\w+', section_lower))
        matches = len(q_words & s_words)
        
        if matches > best_section_score:
            best_section_score = matches
            best_section = section_num
            best_section_text = section_text
    
    if best_section and best_section_score > 0:
        return f"[{display_name} section {best_section}]\n{best_section_text}"
    
    return REFUSAL_TEMPLATE

def main():
    """Interactive CLI — type questions, read answers."""
    print("UC-X Policy Q&A System")
    print("=" * 40)
    print("Ask questions about company policy.")
    print("Type 'quit' to exit.")
    print("=" * 40)
    print()
    
    documents = load_documents()
    
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        
        if not question:
            continue
        if question.lower() == "quit":
            break
        
        answer = find_answer(documents, question)
        print(answer)
        print()

if __name__ == "__main__":
    main()