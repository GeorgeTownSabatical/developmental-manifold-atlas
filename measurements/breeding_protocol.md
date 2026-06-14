# Animal Breeding and Generational Protocol v0.1

## Purpose

This protocol captures generational and selection context for comparative animal studies. It supports hypotheses about coupled deformation of craniofacial geometry, reproductive morphology, fertility, and behavior across breeding lines.

## Required Fields

| Field | Purpose |
| --- | --- |
| generation_id | Breeding generation or timepoint |
| lineage_id | Family, strain, breed, or colony identifier |
| selection_pressure | Selected trait such as tameness, fertility, morphology, growth, or behavior |
| breeding_method | Natural, artificial selection, lab breeding, or managed herd/flock |
| breed_strain | Breed, strain, or population |
| inbreeding_coefficient | Genetic relatedness estimate when available |
| litter_size | Reproductive output |
| survival_rate | Offspring survival |
| age_at_reproduction | Reproductive timing |

## Privacy and Ethics

Individual animal pedigree records may be sensitive for partner institutions or commercial breeding programs. Public records should use open animal data, aggregate summaries, synthetic examples, or controlled-access pointers.

## Reporting Template

Each generational record should link to organism records, measurement records, and any selection-pressure metadata. Parent identifiers should be generalized or controlled-access unless explicitly public.

