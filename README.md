# csv-quality-checker

Validate CSV data against a small JSON schema and produce structured issue reports.

A small, dependency-free Python project designed to be useful on its own and easy
for coding agents to understand. Runs locally; no API keys or services required.

## Quick start

Requires Python 3.11 or newer. From the repository root:

```sh
python -m csv_quality examples/people.csv examples/schema.json
python -m unittest discover -s tests -v
```

Optional installation in a virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
csv-quality-checker --help
```

## Behavior and limits

The JSON schema maps column names to `type`, `required` and `unique` rules.
Types: string (default), integer, finite number and ISO date (YYYY-MM-DD).
Values are stripped before validation; blank optional values are skipped.
Uniqueness compares stripped strings, so `01` and `1` differ. Extra columns are allowed.
Rows are logical CSV records (header is row 1), including multiline records.
The reader streams rows; uniqueness tracking grows with distinct values.
Exit codes: 0 valid, 1 validation issues, 2 malformed input/schema or I/O error.

## Layout

- `csv_quality/core.py`: public functions and command-line interface.
- `tests/`: unit and command-line regression tests.
- `examples/`: small, synthetic inputs safe to share publicly.
- `AGENTS.md`: orientation and working conventions for coding agents.
- `docs/architecture.md`: data flow and extension points.

## Possible next steps

- Add enum and range rules.
- Add issue count limits for very large files.
- Add a Markdown report format.

These are suggestions for future work, not implemented features.

## Development

Tests use the Python standard library. The CI workflow runs them on Python 3.11
and 3.12. Keep changes focused and add regression tests for behavior changes.
The project is intentionally small; it does not claim production readiness.

## License

MIT. See [LICENSE](LICENSE).
