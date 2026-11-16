"""Check CSV headers, row widths, required fields, types and unique values."""
import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re

def validate_schema(schema: dict) -> dict:
    if not isinstance(schema, dict) or not schema:
        raise ValueError("schema must be a non-empty object of column rules")
    for name, rules in schema.items():
        if not isinstance(rules, dict) or set(rules) - {"type", "required", "unique"}:
            raise ValueError(f"invalid rules for {name}")
        if rules.get("type", "string") not in {"string", "integer", "number", "date"}:
            raise ValueError(f"unsupported type for {name}")
        if any(type(rules[key]) is not bool for key in ("required", "unique") if key in rules):
            raise ValueError(f"required and unique must be booleans for {name}")
    return schema

def valid_type(value: str, kind: str) -> bool:
    try:
        if kind == "integer":
            return re.fullmatch(r"[+-]?[0-9]+", value) is not None
        if kind == "number":
            return Decimal(value).is_finite()
        if kind == "date":
            return bool(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)) and bool(date.fromisoformat(value))
        return True
    except (ValueError, InvalidOperation):
        return False

def check_csv(path: Path, schema: dict) -> list[dict]:
    schema = validate_schema(schema)
    issues = []
    seen = {name: set() for name in schema}
    def issue(row, column, code):
        issues.append({"row": row, "column": column, "code": code})
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        headers = next(reader, [])
        if not headers or len(headers) != len(set(headers)):
            raise ValueError("CSV must have a non-empty header with unique column names")
        for name in schema:
            if name not in headers:
                issue(1, name, "missing_column")
        for row_number, values in enumerate(reader, 2):
            if len(values) != len(headers):
                issue(row_number, None, "row_width")
                continue
            row = dict(zip(headers, values))
            for name, rules in schema.items():
                if name not in row:
                    continue
                value = row[name].strip()
                if not value:
                    if rules.get("required"):
                        issue(row_number, name, "required")
                    continue
                if not valid_type(value, rules.get("type", "string")):
                    issue(row_number, name, "invalid_type")
                if rules.get("unique") and value in seen[name]:
                    issue(row_number, name, "duplicate")
                seen[name].add(value)
    return issues

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("schema", type=Path)
    args = parser.parse_args(argv)
    try:
        issues = check_csv(args.csv, json.loads(args.schema.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    return int(bool(issues))
