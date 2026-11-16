from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from csv_quality.core import check_csv, valid_type, validate_schema

class QualityTests(unittest.TestCase):
    def check(self, text, schema):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            path.write_text(text, encoding="utf-8")
            return check_csv(path, schema)

    def test_required_type_and_unique(self):
        issues = self.check("id,age\na,12\na,no\n,3\n", {
            "id": {"required": True, "unique": True}, "age": {"type": "integer"}})
        self.assertEqual([x["code"] for x in issues], ["duplicate", "invalid_type", "required"])

    def test_missing_column_and_width(self):
        issues = self.check("id\na,b\n", {"age": {}})
        self.assertEqual([x["code"] for x in issues], ["missing_column", "row_width"])

    def test_duplicate_headers(self):
        with self.assertRaises(ValueError):
            self.check("id,id\na,b\n", {"id": {}})

    def test_dates_and_finite_numbers(self):
        self.assertTrue(valid_type("2024-02-29", "date"))
        for value in ["2023-02-29", "20240229"]:
            self.assertFalse(valid_type(value, "date"))
        for value in ["NaN", "Infinity", "oops"]:
            self.assertFalse(valid_type(value, "number"))

    def test_schema_validation(self):
        for schema in [[], {}, {"id": {"type": "unknown"}}, {"id": {"required": "yes"}}]:
            with self.assertRaises(ValueError):
                validate_schema(schema)

    def test_clean_data(self):
        self.assertEqual(self.check("id,note\n1,\"hello, world\"\n", {"id": {"type": "integer"}}), [])

    def test_cli(self):
        result = subprocess.run([sys.executable, "-m", "csv_quality", "examples/people.csv",
                                 "examples/schema.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
