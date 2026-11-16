# Architecture

`python -m csv_quality` delegates to `core.main`. Argument parsing and filesystem
access live at the boundary; the exported core functions own the behavior.
Results are plain Python data structures that can be serialized as JSON.

## Design decisions

- Standard library only: easy to run in a fresh agent environment.
- Explicit validation: bad input should fail predictably rather than be coerced.
- Stable ordering: examples and tests stay reproducible across machines.
- Read-only processing: input files are never modified.

## Extension strategy

Add a focused core function, test it using synthetic fixtures, then expose it via
the CLI. Keep the documented default behavior compatible where possible.

## Scope

The JSON schema maps column names to `type`, `required` and `unique` rules.
Types: string (default), integer, finite number and ISO date (YYYY-MM-DD).
Values are stripped before validation; blank optional values are skipped.
Uniqueness compares stripped strings, so `01` and `1` differ. Extra columns are allowed.
Rows are logical CSV records (header is row 1), including multiline records.
The reader streams rows; uniqueness tracking grows with distinct values.
Exit codes: 0 valid, 1 validation issues, 2 malformed input/schema or I/O error.
