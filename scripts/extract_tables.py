import sys
import re
from collections import defaultdict

def extract_tables(sql_content):
    # 1. Identify created temp tables
    created_tables = set(re.findall(r"create\s+(?:temporary\s+|temp\s+)?table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_\.]+)", sql_content, re.IGNORECASE))
    
    # 2. Find COPY ... FROM statements (e.g. S3 files)
    copy_sources = re.findall(r"\bCOPY\s+([a-zA-Z0-9_\.]+)\s+FROM\s+'([^']+)'", sql_content, re.IGNORECASE)

    # 3. Strip SQL comments
    # Single-line comments
    clean_sql = re.sub(r"--[^\n]*", "", sql_content)
    # Multi-line comments
    clean_sql = re.sub(r"/\*.*?\*/", "", clean_sql, flags=re.DOTALL)

    # 4. Handle SQL functions that contain 'FROM' keyword
    # e.g., SUBSTRING(... FROM ...), EXTRACT(... FROM ...), TRIM(... FROM ...)
    clean_sql = re.sub(r"\bSUBSTRING\s*\([^)]*?\bFROM\b[^)]*?\)", "", clean_sql, flags=re.IGNORECASE)
    clean_sql = re.sub(r"\bEXTRACT\s*\([^)]*?\bFROM\b[^)]*?\)", "", clean_sql, flags=re.IGNORECASE)
    clean_sql = re.sub(r"\bTRIM\s*\([^)]*?\bFROM\b[^)]*?\)", "", clean_sql, flags=re.IGNORECASE)

    # 5. Extract tables after FROM, JOIN, or DELETE FROM
    pattern = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_\"\.]+)", re.IGNORECASE)
    matches = pattern.findall(clean_sql)

    raw_tables = set()
    ignored_keywords = {'select', 'values', 'generate_series', 'unnest', 'lateral', 'position'}

    for m in matches:
        t = m.strip('"').strip()
        if not t or t.lower() in ignored_keywords:
            continue
        # Exclude temp tables
        if t.lower().startswith("lp_data_temp.") or t.lower().startswith("lp_dev.lp_data_temp."):
            continue
        if t in created_tables:
            continue
        raw_tables.add(t)

    # Group by schema
    grouped = defaultdict(list)
    for t in sorted(raw_tables):
        parts = t.split(".", 1)
        if len(parts) == 2:
            schema, tbl = parts
            grouped[schema].append(t)
        else:
            grouped["other"].append(t)

    return grouped, copy_sources

def format_output(grouped, copy_sources):
    lines = []
    for schema in sorted(grouped.keys()):
        lines.append(f"### **`{schema}`**")
        for table in sorted(grouped[schema]):
            lines.append(f"- `{table}`")
        lines.append("")

    if copy_sources:
        lines.append("> [!NOTE]")
        lines.append("> External data sources ingested via `COPY ... FROM`:")
        for target, s3_path in copy_sources:
            lines.append(f"> - `{s3_path}` (loaded into `{target}`)")
        lines.append("")

    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_tables.py <path_to_sql_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    grouped, copy_sources = extract_tables(content)
    print(format_output(grouped, copy_sources))
