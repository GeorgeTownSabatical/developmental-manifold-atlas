from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REGISTRY_FILES = {
    "datasets": ("registry/datasets.json", "schemas/dataset.schema.json"),
    "institutions": ("registry/institutions.json", "schemas/institution.schema.json"),
    "contributors": ("registry/contributors.json", "schemas/contributor.schema.json"),
    "instruments": ("registry/instruments.json", "schemas/instrument.schema.json"),
    "hypotheses": ("hypotheses/hypotheses.json", "schemas/hypothesis.schema.json"),
    "demo_records": ("data/demo/developmental_state_objects.json", "schemas/developmental-state-object.schema.json"),
    "organisms": ("data/demo/organisms.json", "schemas/organism.schema.json"),
    "measurements": ("data/demo/measurements.json", "schemas/measurement.schema.json"),
    "landmarks": ("registry/landmarks.json", "schemas/landmark.schema.json"),
    "equivalence_classes": ("registry/equivalence_classes.json", "schemas/equivalence-class.schema.json"),
    "derived_variables": ("registry/derived_variables.json", "schemas/derived-variable.schema.json"),
    "protocol_readiness": ("registry/protocol_readiness.json", "schemas/protocol-readiness.schema.json"),
}


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_file(data_path: Path, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    payload = load_json(data_path)
    return [f"{data_path}: {error}" for error in validate_value(payload, schema)]


def validate_value(value: object, schema: dict[str, object], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "oneOf" in schema:
        branches = schema["oneOf"]
        if isinstance(branches, list) and not any(not validate_value(value, branch, path) for branch in branches if isinstance(branch, dict)):
            return [f"{path}: value does not match any allowed form"]
        return []

    expected_type = schema.get("type")
    if expected_type and not type_matches(value, expected_type):
        return [f"{path}: expected {expected_type}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} is not an allowed value"]

    if isinstance(value, str):
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and not re.search(pattern, value):
            errors.append(f"{path}: {value!r} does not match {pattern}")
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            errors.append(f"{path}: string is shorter than {min_length}")

    if isinstance(value, (int, float)):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{path}: {value} is less than {minimum}")
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(f"{path}: {value} is greater than {maximum}")

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            errors.append(f"{path}: array has fewer than {min_items} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate_value(item, item_schema, f"{path}.{index}"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if isinstance(key, str) and key not in value:
                    errors.append(f"{path}: missing required field {key}")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, child in properties.items():
                if key in value and isinstance(child, dict):
                    errors.extend(validate_value(value[key], child, f"{path}.{key}"))
            if schema.get("additionalProperties") is False:
                allowed = set(properties)
                for key in value:
                    if key not in allowed:
                        errors.append(f"{path}: unexpected field {key}")

    return errors


def type_matches(value: object, expected_type: object) -> bool:
    if isinstance(expected_type, list):
        return any(type_matches(value, item) for item in expected_type)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    return True


def validate_command(_: argparse.Namespace) -> int:
    all_errors: list[str] = []
    for name, (data_rel, schema_rel) in REGISTRY_FILES.items():
        errors = validate_file(ROOT / data_rel, ROOT / schema_rel)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"ok: {name}")

    privacy_errors = privacy_scan(ROOT / "data")
    all_errors.extend(privacy_errors)
    all_errors.extend(ethics_by_schema_checks())

    if all_errors:
        for error in all_errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print("validation complete")
    return 0


def privacy_scan(data_root: Path) -> list[str]:
    flagged_terms = {
        "ssn",
        "social_security",
        "date_of_birth",
        "dob",
        "medical_record_number",
        "mrn",
        "patient_name",
        "address",
        "phone",
        "email",
    }
    errors: list[str] = []
    for path in data_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".csv", ".tsv", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            hits = sorted(term for term in flagged_terms if term in text)
            if hits:
                errors.append(f"{path}: possible sensitive identifiers: {', '.join(hits)}")
    return errors


def ethics_by_schema_checks() -> list[str]:
    datasets = load_json(ROOT / "registry/datasets.json")
    organisms = load_json(ROOT / "data/demo/organisms.json")
    measurements = load_json(ROOT / "data/demo/measurements.json")
    errors: list[str] = []

    dataset_by_id = {dataset["dataset_id"]: dataset for dataset in datasets}
    organism_by_id = {organism["organism_id"]: organism for organism in organisms}
    sensitive_traits = {
        "GWAS_SUMMARY",
        "POLYGENIC_SCORE",
        "COPY_NUMBER_VARIANT",
        "PATHWAY_SCORE",
        "GENE_EXPRESSION",
        "EPIGENETIC_MARKERS",
        "HERITABILITY_ESTIMATE",
        "treatment_type",
        "stimulation_protocol",
        "oocyte_count",
        "mature_oocyte_count",
        "fertilization_rate",
        "embryo_grade",
        "blastocyst_rate",
        "euploid_rate",
        "implantation",
        "clinical_pregnancy",
        "live_birth",
        "miscarriage",
        "neonatal_outcome",
    }

    for dataset in datasets:
        if dataset["access_tier"] == "public" and dataset["data_level"] == "individual" and "human" in " ".join(dataset["species"]).lower():
            errors.append(f"{dataset['dataset_id']}: human individual-level data cannot be public")

    for organism in organisms:
        if organism["species"] == "Homo sapiens" and organism["record_type"] == "individual" and organism["ethics_status"] != "synthetic":
            errors.append(f"{organism['organism_id']}: human individual record is not allowed in public demo data")

    for measurement in measurements:
        dataset = dataset_by_id.get(measurement["dataset_id"])
        organism = organism_by_id.get(measurement["organism_id"])
        if not dataset:
            errors.append(f"{measurement['measurement_id']}: unknown dataset_id {measurement['dataset_id']}")
            continue
        if not organism:
            errors.append(f"{measurement['measurement_id']}: unknown organism_id {measurement['organism_id']}")
            continue
        if measurement["unit"] in {"", "unknown"}:
            errors.append(f"{measurement['measurement_id']}: unit must be explicit")
        is_human = organism["species"] == "Homo sapiens" or "human" in organism["species"].lower()
        public_like = measurement["access_tier"] in {"public", "tier_1_public_animal", "tier_2_public_aggregate_human"}
        synthetic = measurement["access_tier"] == "tier_0_synthetic" or organism["record_type"] == "synthetic"
        if is_human and organism["record_type"] == "individual" and public_like and not synthetic:
            errors.append(f"{measurement['measurement_id']}: human individual measurement cannot be public unless synthetic")
        if is_human and measurement["trait_id"] in sensitive_traits and public_like and not synthetic:
            errors.append(f"{measurement['measurement_id']}: sensitive human trait cannot be public unless aggregate or synthetic")

    return errors


def register_command(args: argparse.Namespace) -> int:
    registry_path = ROOT / "registry/datasets.json"
    datasets = load_json(registry_path)
    dataset = {
        "dataset_id": args.dataset_id,
        "title": args.title,
        "version": "0.1.0",
        "contributor": args.contact,
        "description": args.description,
        "species": [args.species],
        "population": args.population,
        "sex": "mixed",
        "age_stage": "unspecified",
        "measurements": [],
        "sample_size": 0,
        "data_level": "metadata-only",
        "access_tier": "metadata-only",
        "license": "TBD",
        "ethics_status": "pending",
        "institution_id": args.institution_id,
        "contact": args.contact,
        "citation": args.citation,
        "provenance": "registered through dmatlas CLI",
        "limitations": "metadata-only placeholder pending review",
        "update_frequency": "unknown",
        "quality_score": 0,
    }
    datasets.append(dataset)
    registry_path.write_text(json.dumps(datasets, indent=2) + "\n", encoding="utf-8")
    print(f"registered dataset: {args.dataset_id}")
    return 0


def normalize_command(_: argparse.Namespace) -> int:
    records = load_json(ROOT / "data/demo/developmental_state_objects.json")
    normalized = []
    for record in records:
        measurements = record.get("measurements", {})
        agd = measurements.get("agd_mm")
        mass = measurements.get("body_mass_g")
        item = dict(record)
        if agd is not None and mass:
            item["derived"] = {
                **item.get("derived", {}),
                "agd_norm_mass_cuberoot": round(agd / (mass ** (1 / 3)), 6),
            }
        normalized.append(item)
    out = ROOT / "dashboards/normalized_demo_records.json"
    out.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


def quality_command(_: argparse.Namespace) -> int:
    measurements = load_json(ROOT / "data/demo/measurements.json")
    organisms = load_json(ROOT / "data/demo/organisms.json")

    grades: dict[str, int] = {}
    traits: dict[str, int] = {}
    missingness: dict[str, int] = {}
    access_tiers: dict[str, int] = {}
    stages: dict[str, int] = {}

    organism_by_id = {organism["organism_id"]: organism for organism in organisms}

    for measurement in measurements:
        grades[measurement["quality_flag"]] = grades.get(measurement["quality_flag"], 0) + 1
        traits[measurement["trait_id"]] = traits.get(measurement["trait_id"], 0) + 1
        access_tiers[measurement["access_tier"]] = access_tiers.get(measurement["access_tier"], 0) + 1
        if isinstance(measurement["value"], str) and measurement["value"].startswith("NA_"):
            missingness[measurement["value"]] = missingness.get(measurement["value"], 0) + 1
        organism = organism_by_id.get(measurement["organism_id"], {})
        stage = organism.get("developmental_stage", "unknown")
        stages[stage] = stages.get(stage, 0) + 1

    out = ROOT / "dashboards/data_quality.json"
    out.write_text(
        json.dumps(
            {
                "measurement_count": len(measurements),
                "organism_count": len(organisms),
                "quality_grades": grades,
                "trait_coverage": traits,
                "missingness": missingness,
                "access_tiers": access_tiers,
                "developmental_stages": stages,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


def standards_command(_: argparse.Namespace) -> int:
    landmarks = load_json(ROOT / "registry/landmarks.json")
    equivalence = load_json(ROOT / "registry/equivalence_classes.json")
    derived = load_json(ROOT / "registry/derived_variables.json")
    readiness = load_json(ROOT / "registry/protocol_readiness.json")

    readiness_counts: dict[str, int] = {}
    domains: dict[str, int] = {}
    for item in readiness:
        readiness_counts[item["status"]] = readiness_counts.get(item["status"], 0) + 1
        domains[item["domain"]] = domains.get(item["domain"], 0) + 1

    payload = {
        "phase": "Phase 2",
        "focus": "Measurement standardization",
        "landmark_count": len(landmarks),
        "equivalence_class_count": len(equivalence),
        "derived_variable_count": len(derived),
        "protocol_count": len(readiness),
        "protocol_status": readiness_counts,
        "protocol_domains": domains,
    }
    out = ROOT / "dashboards/standards.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for key, value in payload.items():
        print(f"{key}: {value}")
    return 0


def backend_command(_: argparse.Namespace) -> int:
    datasets = load_json(ROOT / "registry/datasets.json")
    hypotheses = load_json(ROOT / "hypotheses/hypotheses.json")
    measurements = load_json(ROOT / "data/demo/measurements.json")
    readiness = load_json(ROOT / "registry/protocol_readiness.json")

    command_surface = [
        "validate",
        "quality",
        "standards",
        "hypotheses",
        "eligibility",
        "backend",
        "report",
        "analyze",
        "normalize",
        "cite",
        "register",
    ]
    workflow_surface = [
        "schema validation",
        "data quality scoring",
        "protocol readiness export",
        "hypothesis eligibility check",
        "dashboard generation",
        "pages deployment",
    ]
    package_surface = {
        "python": "scaffolded",
        "typescript": "scaffolded",
        "r": "scaffolded",
        "rust": "scaffolded",
        "julia": "scaffolded",
    }
    payload = {
        "phase": "Phase 3",
        "focus": "Developer backend maturity",
        "cli_command_count": len(command_surface),
        "cli_commands": command_surface,
        "workflow_count": len(workflow_surface),
        "workflows": workflow_surface,
        "package_surface": package_surface,
        "dataset_count": len(datasets),
        "hypothesis_count": len(hypotheses),
        "measurement_count": len(measurements),
        "protocol_count": len(readiness),
        "backend_status": "active",
        "next_capabilities": [
            "hypothesis test runner",
            "unit normalization utilities",
            "sensitivity analysis generator",
            "reproducible report export",
            "package API stabilization"
        ],
    }
    out = ROOT / "dashboards/backend.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for key, value in payload.items():
        if key in {"cli_commands", "workflows", "package_surface", "next_capabilities"}:
            continue
        print(f"{key}: {value}")
    return 0


def eligibility_command(_: argparse.Namespace) -> int:
    hypotheses = load_json(ROOT / "hypotheses/hypotheses.json")
    measurements = load_json(ROOT / "data/demo/measurements.json")
    trait_ids = {measurement["trait_id"] for measurement in measurements}
    records = []
    for hypothesis in hypotheses:
        required = set(hypothesis["required_variables"])
        available = sorted(required & trait_ids)
        missing = sorted(required - trait_ids)
        records.append(
            {
                "hypothesis_id": hypothesis["hypothesis_id"],
                "title": hypothesis["title"],
                "evidence_grade": hypothesis["evidence_grade"],
                "available_variables": available,
                "missing_variables": missing,
                "eligibility": "pilot-ready" if available else "not-ready",
            }
        )
    out = ROOT / "dashboards/hypothesis_eligibility.json"
    out.write_text(json.dumps({"records": records}, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(f"{record['hypothesis_id']}: {record['eligibility']} ({len(record['available_variables'])} available, {len(record['missing_variables'])} missing)")
    return 0


def report_command(_: argparse.Namespace) -> int:
    datasets = load_json(ROOT / "registry/datasets.json")
    hypotheses = load_json(ROOT / "hypotheses/hypotheses.json")
    records = load_json(ROOT / "data/demo/developmental_state_objects.json")
    measurements = load_json(ROOT / "data/demo/measurements.json")
    organisms = load_json(ROOT / "data/demo/organisms.json")

    species_counts: dict[str, int] = {}
    measurement_counts: dict[str, int] = {}
    access_tiers: dict[str, int] = {}
    hypothesis_status: dict[str, int] = {}
    evidence_grades: dict[str, int] = {}
    quality_grades: dict[str, int] = {}

    for dataset in datasets:
        access_tiers[dataset["access_tier"]] = access_tiers.get(dataset["access_tier"], 0) + 1
        for species in dataset.get("species", []):
            species_counts[species] = species_counts.get(species, 0) + 1
        for measurement in dataset.get("measurements", []):
            measurement_counts[measurement] = measurement_counts.get(measurement, 0) + 1

    for hypothesis in hypotheses:
        status = hypothesis["status"]
        hypothesis_status[status] = hypothesis_status.get(status, 0) + 1
        grade = hypothesis["evidence_grade"]
        evidence_grades[grade] = evidence_grades.get(grade, 0) + 1

    for measurement in measurements:
        quality_grades[measurement["quality_flag"]] = quality_grades.get(measurement["quality_flag"], 0) + 1

    dashboard = {
        "project": "Developmental Manifold Atlas",
        "version": "0.1.0",
        "dataset_count": len(datasets),
        "hypothesis_count": len(hypotheses),
        "demo_record_count": len(records),
        "organism_count": len(organisms),
        "measurement_record_count": len(measurements),
        "species_counts": species_counts,
        "measurement_counts": measurement_counts,
        "access_tiers": access_tiers,
        "hypothesis_status": hypothesis_status,
        "evidence_grades": evidence_grades,
        "quality_grades": quality_grades,
    }

    out = ROOT / "dashboards/summary.json"
    out.write_text(json.dumps(dashboard, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(dashboard)
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


def write_markdown_report(dashboard: dict[str, object]) -> None:
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    lines = [
        "# Atlas Backend Report",
        "",
        "Generated from repository registries and dashboard JSON.",
        "",
        f"- Datasets: {dashboard['dataset_count']}",
        f"- Hypotheses: {dashboard['hypothesis_count']}",
        f"- Organisms: {dashboard['organism_count']}",
        f"- Measurements: {dashboard['measurement_record_count']}",
        "",
        "## Evidence Grades",
        "",
    ]
    for grade, count in sorted(dashboard["evidence_grades"].items()):
        lines.append(f"- {grade}: {count}")
    lines.extend(["", "## Measurement Quality", ""])
    for grade, count in sorted(dashboard["quality_grades"].items()):
        lines.append(f"- {grade}: {count}")
    (reports_dir / "atlas_backend_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def analyze_command(_: argparse.Namespace) -> int:
    records = load_json(ROOT / "data/demo/developmental_state_objects.json")
    rows = []
    for record in records:
        measurements = record.get("measurements", {})
        agd = measurements.get("agd_mm")
        skull = measurements.get("skull_length_mm")
        snout = measurements.get("snout_length_mm")
        if agd is not None and skull and snout is not None:
            rows.append(
                {
                    "dso_id": record["dso_id"],
                    "agd_mm": agd,
                    "snout_skull_ratio": round(snout / skull, 6),
                }
            )

    out = ROOT / "dashboards/pilot_agd_craniofacial.json"
    out.write_text(json.dumps({"analysis": "pilot_agd_craniofacial", "rows": rows}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


def cite_command(_: argparse.Namespace) -> int:
    datasets = load_json(ROOT / "registry/datasets.json")
    for dataset in datasets:
        print(f"{dataset['dataset_id']}: {dataset['citation']}")
    return 0


def hypotheses_command(_: argparse.Namespace) -> int:
    hypotheses = load_json(ROOT / "hypotheses/hypotheses.json")
    for hypothesis in hypotheses:
        print(f"{hypothesis['hypothesis_id']} [{hypothesis['evidence_grade']}]: {hypothesis['title']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dmatlas")
    sub = parser.add_subparsers(required=True)

    sub.add_parser("validate", help="validate schemas and public-data safety").set_defaults(func=validate_command)
    sub.add_parser("normalize", help="compute demo normalized measures").set_defaults(func=normalize_command)
    sub.add_parser("report", help="generate dashboard-ready summary JSON").set_defaults(func=report_command)
    sub.add_parser("quality", help="generate data-quality dashboard JSON").set_defaults(func=quality_command)
    sub.add_parser("standards", help="generate measurement-standardization dashboard JSON").set_defaults(func=standards_command)
    sub.add_parser("backend", help="generate developer-backend maturity dashboard JSON").set_defaults(func=backend_command)
    sub.add_parser("eligibility", help="check registered hypothesis variable eligibility").set_defaults(func=eligibility_command)
    sub.add_parser("analyze", help="run pilot AGD-craniofacial analysis").set_defaults(func=analyze_command)
    sub.add_parser("cite", help="print dataset citation records").set_defaults(func=cite_command)
    sub.add_parser("hypotheses", help="list registered hypotheses and evidence grades").set_defaults(func=hypotheses_command)

    register = sub.add_parser("register", help="append dataset metadata")
    register.add_argument("--dataset-id", required=True)
    register.add_argument("--title", required=True)
    register.add_argument("--description", required=True)
    register.add_argument("--species", required=True)
    register.add_argument("--population", default="unspecified")
    register.add_argument("--institution-id", required=True)
    register.add_argument("--contact", required=True)
    register.add_argument("--citation", default="TBD")
    register.set_defaults(func=register_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
