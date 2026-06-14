# Developmental Manifold Atlas

Open infrastructure for AGD, craniofacial geometry, fertility, neonatal trajectory, and developmental-field research.

Developmental Manifold Atlas is a forkable research platform for studying whether reproductive anatomy, craniofacial geometry, neonatal growth, fertility outcomes, genetics, endocrine exposure, and environmental context are coupled observables of shared developmental trajectories.

The project provides:

- structured registries for datasets, institutions, contributors, instruments, and hypotheses
- public-safe synthetic/demo data
- JSON schemas for contribution validation
- universal organism and measurement records with units, landmarks, quality flags, missingness codes, and provenance
- a `dmatlas` command-line interface
- reproducible dashboard generation
- GitHub Pages-ready public documentation
- governance, ethics, and contribution workflows

Sensitive individual human records do not belong in this repository. Public content is limited to schemas, metadata, synthetic records, open animal data, aggregate summaries, analysis code, and dashboard-ready outputs.

## Quick Start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
dmatlas validate
dmatlas quality
dmatlas standards
dmatlas hypotheses
dmatlas report
pytest
```

Open `docs/index.html` to view the static portal after `dmatlas report` generates dashboard JSON.

## Repository Map

| Path | Purpose |
| --- | --- |
| `docs` | GitHub Pages portal and public dashboard |
| `schemas` | JSON schemas for registry and data submissions |
| `registry` | datasets, institutions, contributors, instruments |
| `registry/trait_vocabulary.json` | standardized AGD, craniofacial, neonatal, fertility, genetics, exposure, and derived traits |
| `registry/landmarks.json` | Phase 2 landmark definitions |
| `registry/equivalence_classes.json` | Phase 2 comparability grades for cross-species measurements |
| `registry/derived_variables.json` | Phase 2 derived-variable formulas |
| `registry/protocol_readiness.json` | Phase 2 protocol review status |
| `hypotheses` | versioned scientific hypothesis records |
| `measurements` | measurement standards and working group protocols |
| `data` | synthetic and public demo datasets only |
| `pipelines` | validation, harmonization, analysis, dashboard builders |
| `models` | statistical and manifold model scaffolds |
| `cli` | `dmatlas` command-line tool |
| `dashboards` | generated dashboard-ready JSON |
| `governance` | ethics, review, consortium, privacy, and contribution rules |
| `.github` | CI, issue templates, pull request template |

## Core Workflow

1. Register a dataset in `registry/datasets.json`.
2. Add public-safe synthetic/demo records or a controlled-access pointer.
3. Add organism/cohort context and measurement records with explicit units, landmarks, quality, and provenance.
4. Validate schemas with `dmatlas validate`.
5. Generate dashboard summaries with `dmatlas quality` and `dmatlas report`.
6. Submit a pull request.
7. CI checks schema validity, data quality, privacy constraints, tests, and docs.

## Central Hypothesis

Developmental outcomes emerge from a shared developmental state-space. Observable traits such as AGD, skull geometry, fertility markers, neonatal measurements, genetics, endocrine exposure, and environmental context are coordinates within that state-space rather than isolated observations.
