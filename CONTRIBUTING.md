# Contributing

## Dataset Contributions

1. Add or update metadata in `registry/datasets.json`.
2. Add organism or aggregate context records to `data/demo/organisms.json` or a future public-safe dataset file.
3. Add measurement records with explicit trait IDs, units, landmarks, methods, instruments, observer/lab IDs, uncertainty, quality flags, source, access tier, and provenance.
4. Add only public-safe data to `data/`.
5. Keep controlled human data in institutional repositories or controlled-access systems.
6. Run `dmatlas validate`.
7. Run `dmatlas quality`.
8. Run `dmatlas report`.
9. Open a pull request using the project template.

No naked measurements: a value without context, unit, landmark, provenance, quality, and access tier is not ready for the atlas.

## Phase 2 Measurement Standardization

Before a dataset can move beyond metadata-only status, contributors should map measurements to:

- `registry/landmarks.json`
- `registry/equivalence_classes.json`
- `registry/derived_variables.json`
- `registry/protocol_readiness.json`

Use `examples/phase_two_standardization_checklist.md` before opening a pull request.

## Hypothesis Contributions

Add a structured hypothesis to `hypotheses/hypotheses.json` with required variables, correction factors, primary test, eligible datasets, replication threshold, status, and confidence.

## Measurement Standards

Protocol changes should name landmarks, units, observer requirements, instrument constraints, and known limitations.
