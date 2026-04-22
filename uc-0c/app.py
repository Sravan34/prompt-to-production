"""
UC-0C app.py — Budget Growth Calculation Agent
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from pathlib import Path

def load_dataset(file_path: str) -> dict:
    """
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    required_columns = ['period', 'ward', 'category', 'budgeted_amount', 'actual_spend', 'notes']
    if not rows:
        raise ValueError("CSV is empty")
    
    for col in required_columns:
        if col not in rows[0]:
            raise ValueError(f"Missing required column: {col}")
    
    null_rows = []
    for i, row in enumerate(rows):
        if row['actual_spend'].strip() == '':
            null_rows.append({
                'row_num': i + 2,
                'period': row['period'],
                'ward': row['ward'],
                'category': row['category'],
                'notes': row['notes']
            })
    
    return {
        'data': rows,
        'columns': required_columns,
        'null_count': len(null_rows),
        'null_rows': null_rows
    }

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    """
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    for i, row in enumerate(filtered):
        period = row['period']
        actual_spend_str = row['actual_spend'].strip()
        
        if actual_spend_str == '':
            results.append({
                'period': period,
                'actual_spend': 'NULL',
                'growth_pct': 'NULL - FLAGGED (do not compute)',
                'formula': 'N/A - null value',
                'notes': row['notes']
            })
            continue
        
        actual_spend = float(actual_spend_str)
        
        if i == 0:
            growth_pct = 'N/A - first period'
            formula = 'N/A'
        else:
            prev_row = filtered[i - 1]
            prev_spend_str = prev_row['actual_spend'].strip()
            
            if prev_spend_str == '':
                growth_pct = 'NULL - FLAGGED (prev is null)'
                formula = 'N/A - cannot compute with null'
            else:
                prev_spend = float(prev_spend_str)
                if growth_type == 'MoM':
                    if prev_spend != 0:
                        growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                        formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                    else:
                        growth_pct = 'DIVBYZERO'
                        formula = 'Division by zero'
                elif growth_type == 'YoY':
                    if i >= 12 and filtered[i - 12]['actual_spend'].strip():
                        prev_spend = float(filtered[i - 12]['actual_spend'])
                        if prev_spend != 0:
                            growth_pct = ((actual_spend - prev_spend) / prev_spend) * 100
                            formula = f"(({actual_spend} - {prev_spend}) / {prev_spend}) * 100"
                        else:
                            growth_pct = 'DIVBYZERO'
                            formula = 'Division by zero'
                    else:
                        growth_pct = 'N/A - no 12-month lag'
                        formula = 'N/A'
                else:
                    growth_pct = 'INVALID'
                    formula = 'Invalid growth_type'
        
        if isinstance(growth_pct, float):
            growth_pct = f"{growth_pct:.1f}%"
        
        results.append({
            'period': period,
            'actual_spend': actual_spend,
            'growth_pct': growth_pct,
            'formula': formula,
            'notes': row['notes']
        })
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Calculate budget growth')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--ward', required=True, help='Ward name (e.g., "Ward 1 – Kasba")')
    parser.add_argument('--category', required=True, help='Category name')
    parser.add_argument('--growth-type', required=True, help='Growth type: MoM or YoY')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    
    args = parser.parse_args()
    
    if args.growth_type not in ['MoM', 'YoY']:
        print(f"Error: --growth-type must be MoM or YoY, got: {args.growth_type}", file=sys.stderr)
        sys.exit(1)
    
    try:
        dataset = load_dataset(args.input)
        
        print(f"Loaded {len(dataset['data'])} rows, {dataset['null_count']} null values found:")
        for nr in dataset['null_rows']:
            print(f"  - Row {nr['row_num']}: {nr['period']} | {nr['ward']} | {nr['category']} | {nr['notes']}")
        
        results = compute_growth(dataset['data'], args.ward, args.category, args.growth_type)
        
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['period', 'actual_spend', 'growth_pct', 'formula', 'notes'])
            for r in results:
                writer.writerow([
                    r['period'],
                    r['actual_spend'],
                    r['growth_pct'],
                    r['formula'],
                    r['notes']
                ])
        
        print(f"Output written to: {output_path}")
        
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