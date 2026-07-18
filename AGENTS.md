# Contributor Guide

## Scope

This repository analyses synthetic, hourly residential-energy data for Dubai homes. Keep raw input data immutable; write derived files only to `data/processed/`.

## Conventions

- Use Python 3.10+ and type hints for new reusable code.
- Put reusable application code in `src/smart_energy_analytics/` and tests in `tests/`.
- Use `snake_case` for files, functions, variables, and dataframe columns.
- Keep energy values in kWh, AC use in minutes per hour, and timestamps in Gulf Standard Time (`Asia/Dubai`) unless a field states otherwise.
- Do not add real household identifiers or personal information.

## Verification

Before submitting code changes, run:

```bash
python -m pytest
```

For data transformations, also verify required columns, non-negative consumption, occupancy counts, and AC durations from 0 to 60 minutes.
