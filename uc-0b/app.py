"""
UC-0B app.py — Policy Summarization Agent
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys
from pathlib import Path

def retrieve_policy(file_path: str) -> dict:
    """
    Loads policy .txt file and returns content as structured numbered sections.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    if path.suffix != '.txt':
        raise ValueError(f"Expected .txt file, got: {path.suffix}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s', line.strip())
        if match:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = match.group(1)
            current_content = [line.strip()]
        elif current_section:
            current_content.append(line.strip())
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary with clause references.
    """
    target_clauses = [
        '2.3', '2.4', '2.5', '2.6', '2.7',
        '3.2', '3.4',
        '5.2', '5.3',
        '7.2'
    ]
    
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append("")
    
    for clause in target_clauses:
        if clause in sections:
            content = sections[clause]
            summary_lines.append(f"Clause {clause}:")
            summary_lines.append(content)
            summary_lines.append("")
        else:
            summary_lines.append(f"Clause {clause}: [NOT FOUND]")
            summary_lines.append("")
    
    return '\n'.join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description='Summarize HR Leave Policy')
    parser.add_argument('--input', required=True, help='Input policy .txt file path')
    parser.add_argument('--output', required=True, help='Output summary file path')
    
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to: {output_path}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()