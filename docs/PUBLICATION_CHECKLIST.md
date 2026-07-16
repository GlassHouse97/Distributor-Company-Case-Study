# Publication Checklist

The analytical work, public dataset, and portfolio deliverables are complete. Use this checklist before making the repository public.

## Data Package

- [x] Include the seven scrubbed annual transaction CSVs in `data/transactions/`.
- [x] Include the scrubbed `CustomerData.csv`, customer-class map, and schema reference.
- [x] Document that financial values are scaled portfolio values rather than the source company's actual results.
- [x] Verify every public transaction file against `data/metadata/source_manifest.json`.
- [x] Exclude the original identifying exports, scrub workbook, quarterly duplicates, legacy analysis files, and local SQLite database.
- [x] Replace source customer numbers in public analysis outputs with stable labels.

## Repository Validation

- [ ] Run `python scripts/convert_csv_to_utf8.py` and confirm strict UTF-8 validation.
- [ ] Run `python scripts/prepare_reference_data.py`.
- [ ] Run `python scripts/build_final_database.py`.
- [ ] Run `python scripts/validate_final_database.py` and confirm every data-quality check passes.
- [ ] Run `python scripts/analyze_q1.py`.
- [ ] Run `python scripts/analyze_q2_q4.py` and confirm every question-level check passes.
- [ ] Regenerate and visually inspect the Word report.
- [ ] Open and visually inspect every Excel workbook sheet.
- [ ] Confirm every root README link works from the repository landing page.

## Public Release

- [ ] Make the repository public.
- [ ] Open the repository while signed out and verify that every file and link is accessible.
- [ ] Confirm that the repository landing page clearly presents Read, Download, and Reproduce paths.
- [ ] Consider adding a formal code and data license before inviting reuse beyond portfolio reproduction.
- [ ] Tag the first public version, such as `v1.0.0`, after a clean-clone reproduction test.

## Portfolio Review

- [ ] Read the executive summary on a phone-sized screen and on desktop.
- [ ] Verify that no chart or screenshot exposes source-company names or private paths.
- [ ] Ask one non-technical reviewer to explain the business story after a two-minute scan.
- [ ] Ask one technical reviewer to rebuild the database and run at least one SQL analysis from a clean environment.

## Current Status

The repository is structured as a fully reproducible portfolio project with public, anonymized, scaled data. The remaining publication step is to complete the checks above and change the GitHub repository visibility to public.
