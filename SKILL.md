---
name: extract-sql-tables
description: Extracts all raw database tables used in the currently active or specified SQL file/query from FROM and JOIN clauses, excluding temporary tables. Use whenever the user asks to list, extract, or get tables from a SQL query, or invokes /extract-sql-tables.
---

# Extract SQL Tables

This skill extracts all raw database tables referenced across `FROM` and `JOIN` clauses in a SQL query or script, excluding temporary tables and non-table syntax.

## When to Run

- When the user runs `/extract-sql-tables`
- When the user asks to extract, list, or find tables used in the open SQL file or query

## Guidelines & Rules

1. **Target File / Context**:
   - Identify the user's currently active document in the editor (or the file/query text specified by the user).
   - If not specified, check the active document in the environment metadata.

2. **Parsing Rules**:
   - Scan for table references in `FROM` and `JOIN` (e.g., `LEFT JOIN`, `RIGHT JOIN`, `INNER JOIN`, `FULL JOIN`, `CROSS JOIN`, `JOIN`) statements.
   - Include tables in subqueries, CTEs, and `DELETE FROM` statements.
   - **Exclude temporary tables**:
     - Any tables with schema consist of name `temp.` or `dev.` 
     - Any tables created within the query as temporary tables (e.g. `CREATE TABLE lp_data_temp....`, `CREATE TEMP TABLE ...`)
   - **Exclude SQL functions that use the `FROM` keyword**:
     - `SUBSTRING(... FROM ...)`
     - `EXTRACT(... FROM ...)`
     - `TRIM(... FROM ...)`
   - Exclude subquery parentheses or keywords like `(SELECT ...)` or `VALUES`.

3. **Output Format**:
   - Present the tables in clean **bullet point format** (`- `).
   - Group the tables by schema name for clear readability.
   - If there are external data sources (such as Redshift `COPY ... FROM 's3://...'`), mention them separately under a note.

## Automation Script

A helper Python script is available at `./scripts/extract_tables.py` to automatically parse and extract tables from a SQL file:

```powershell
python "~/.gemini/config/skills/extract-sql-tables/scripts/extract_tables.py" "<path_to_sql_file>"
```
