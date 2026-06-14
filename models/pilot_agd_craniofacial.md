# Pilot AGD-Craniofacial Model

The first analysis target is `H-AGD-FACE-001`.

Minimum variables:

- AGD
- body mass or body size proxy
- skull length
- snout length or facial length
- sex
- age or developmental stage
- species

Initial derived values:

- `AGD_norm = AGD / body_mass^(1/3)`
- `Face_ratio = snout_length / skull_length`

The v0.1 CLI writes a simple dashboard-ready pilot table. Later releases should add residualization, hierarchical models, phylogenetic correction, and sensitivity analysis.

