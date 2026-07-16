# Publication Checklist

This file separates checks that have been completed in the repository from the final release and human-review steps that still need the repository owner.

## Data Package

- [x] Include the seven scrubbed annual transaction CSVs in `data/transactions/`.
- [x] Include the scrubbed `CustomerData.csv`, customer-class map, and schema reference.
- [x] State that the financial values are anonymized, scaled portfolio values rather than the source company's actual results.
- [x] Verify every public transaction file against `data/metadata/source_manifest.json`.
- [x] Exclude identifying exports, the scrub workbook, quarterly duplicates, old analysis files, and the local SQLite database.
- [x] Replace source customer numbers in public analysis outputs with stable labels.

## Repository Validation

Completed on July 16, 2026 with the bundled project Python runtime.

- [x] Run `python scripts/verify_source_files.py`; all seven annual files match the published checksum manifest.
- [x] Run `python scripts/convert_csv_to_utf8.py --check-only`; every public CSV passes strict UTF-8 decoding.
- [x] Run `python scripts/prepare_reference_data.py`; the 66 source mappings plus the added `Legacy Customer` mapping are present.
- [x] Run `python scripts/build_final_database.py`; the database rebuilt from all seven annual files with 3,714,624 transaction rows.
- [x] Run `python scripts/validate_final_database.py`; every database and edge-case check passes.
- [x] Run `python scripts/analyze_q1.py`; every Question 1 validation check passes.
- [x] Run `python scripts/analyze_q2.py`; every Question 2 validation check passes.
- [x] Run `python scripts/analyze_q3.py`; every Question 3 validation check passes.
- [x] Run `python scripts/analyze_q4.py`; every Question 4 validation check passes after excluding the four partial 2017 rows from the complete-year trend.
- [x] Run the maintenance helpers: source-manifest generation, source verification, public-label sanitization, and a read-only database query.
- [x] Compile all 13 Python scripts without syntax errors.
- [x] Regenerate the Word report and inspect all eight rendered pages.
- [x] Regenerate the Excel analysis workbook, scan for formula errors, and inspect all ten rendered sheets.
- [x] Confirm every relative link in the root README resolves to an existing file or folder.
- [x] Search the repository text, Word package, and Excel package for private machine paths and source-company identifiers; none were found.

## Public Release

- [ ] Change the GitHub repository visibility to public. This remains an owner decision and has not been changed automatically.
- [ ] Open the public repository while signed out and verify that every file and link is accessible.
- [x] Confirm that the repository landing page clearly presents Read, Download, and Reproduce paths.
- [x] Consider a formal code and data license. The current decision is recorded as `No separate data license selected`; select one before granting reuse rights beyond portfolio review and reproduction.
- [ ] Tag the first public version, such as `v1.0.0`, after the signed-out and clean-clone checks pass.

## Portfolio Review

- [ ] Read the GitHub executive summary at desktop and phone widths after the revised files are pushed.
- [x] Verify that the report, workbook, and charts do not expose source-company names or private machine paths.
- [ ] Ask one non-technical reviewer to explain the business story after a two-minute scan.
- [ ] Ask one technical reviewer to rebuild the database and run at least one SQL analysis from a clean environment.

## Current Status

The repository's data, scripts, analysis outputs, Word report, Excel workbook, links, and privacy checks are complete. The project should remain in pre-publication status until the owner completes the public-visibility, signed-out access, version-tag, and two human-review checks above.
