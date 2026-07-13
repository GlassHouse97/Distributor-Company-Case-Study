# Publication Checklist

The analytical work and portfolio deliverables are complete. Use this checklist before making the repository public.

## Required Before Release

- [ ] Select an external host for the seven annual transaction CSVs.
- [ ] Add the stable dataset URL and download instructions to `data/README.md` and the root `README.md`.
- [ ] Choose and publish a data license that explicitly permits public redistribution and portfolio use.
- [ ] Verify every hosted transaction file against `data/metadata/source_manifest.json`.
- [x] Exclude the identifying `CustomerData.csv` supplement from the public tree.
- [x] Confirm that no private customer export, scrub workbook, quarterly duplicate, local SQLite database, Office lock file, or machine-specific path is staged for publication.
- [x] Replace source customer numbers in concentration, lifecycle, outreach, and workbook outputs with stable public labels.

## Repository Validation

- [ ] Run `python scripts/convert_csv_to_utf8.py` and confirm strict UTF-8 validation.
- [ ] Run `python scripts/prepare_reference_data.py`.
- [ ] Run `python scripts/build_canonical_database.py`.
- [ ] Run `python scripts/validate_canonical_database.py` and confirm every canonical check passes.
- [ ] Run `python scripts/analyze_q1.py`.
- [ ] Run `python scripts/analyze_q2_q4.py` and confirm every question-level check passes.
- [ ] Confirm the root README links work from the repository landing page.
- [ ] Confirm that the Word report and Excel workbook open correctly after cloning or downloading the repository.

## GitHub Release Package

- [ ] Include `README.md`, `CASE_STUDY_QUESTIONS.md`, `docs/`, `scripts/`, `SOLUTION/`, approved reference data, metadata, and `deliverables/`.
- [ ] Exclude `data/raw/transactions/*.csv`, local databases, private references, local archives, and QA render artifacts.
- [ ] Add the external dataset URL, version, file sizes, SHA-256 checksums, and license to the release notes.
- [ ] Tag the first public version, such as `v1.0.0`, only after a clean-clone reproduction test.

## Portfolio Review

- [ ] Open the repository while signed out to verify that every public link is accessible.
- [ ] Read the executive summary on a phone-sized screen and on desktop.
- [ ] Verify that no chart or screenshot exposes customer names or private source paths.
- [ ] Ask one non-technical reviewer to explain the business story after a two-minute scan.
- [ ] Ask one technical reviewer to rebuild the database and run at least one SQL analysis from a clean environment.

## Current Release Blockers

As of July 13, 2026, the GitHub portfolio package is privacy-safe and ready to publish. Full raw-data reproduction remains blocked on an approved external dataset URL, de-identification review, and a redistribution license. The analysis itself is complete and validated.
