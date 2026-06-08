import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

REQUIRED_FIELDS = [
    "commandInvocation",
    "sourceDatabasePath",
    "backupArtifactPath",
    "rehearsalArtifactPath",
    "stdout",
    "stderr",
    "rehearsalJson",
    "observedStopCondition",
    "operatorEscalationNote",
]

REQUIRED_REHEARSAL_JSON_FIELDS = [
    "preMigrationCounts",
    "postMigrationCounts",
    "postMigrationRows",
    "readbackPostIds",
]

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{8,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{8,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{16,}", re.IGNORECASE),
    re.compile(r"__SECRET_LIKE__"),
]


def _base_result(*, status: str, reason: str, policy_code: str | None, recommended_next_action: str) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "policyCode": policy_code,
        "validatedArtifacts": {},
        "observedCounts": {},
        "observedMigrationRows": [],
        "observedReadbackPostIds": [],
        "recommendedNextAction": recommended_next_action,
    }


def _refused(reason: str, policy_code: str = "invalid_evidence_bundle") -> dict[str, Any]:
    return _base_result(
        status="refused",
        reason=reason,
        policy_code=policy_code,
        recommended_next_action="Fix the evidence bundle and rerun dry-run analysis; do not mutate databases.",
    )


def _stringify_for_scan(value: object) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _contains_secret_like_value(bundle: Mapping[str, Any]) -> bool:
    serialized = _stringify_for_scan(bundle)
    return any(pattern.search(serialized) for pattern in SECRET_PATTERNS)


def _resolve_existing_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value).resolve()
    if not path.exists():
        return None
    return path


def _migration_rows_include_schema_migrations(rows: object) -> bool:
    if not isinstance(rows, list):
        return False
    for row in rows:
        if not isinstance(row, list | tuple) or len(row) != 2:
            return False
        migration_id, migration_name = row
        if migration_id == 1 and isinstance(migration_name, str) and migration_name:
            return True
    return False


def _counts_are_consistent(rehearsal_json: Mapping[str, Any]) -> bool:
    pre_counts = rehearsal_json.get("preMigrationCounts")
    post_counts = rehearsal_json.get("postMigrationCounts")
    if not isinstance(pre_counts, dict) or not isinstance(post_counts, dict):
        return False
    return pre_counts == post_counts


def analyze_evidence_bundle(evidence: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in evidence]
    if missing:
        return _refused(f"Evidence bundle missing required field: {missing[0]}", "missing_evidence_field")

    if _contains_secret_like_value(evidence):
        return _refused("Evidence bundle contains secret-like text and cannot be analyzed safely.", "secret_like_evidence")

    source_path = _resolve_existing_path(evidence.get("sourceDatabasePath"))
    backup_path = _resolve_existing_path(evidence.get("backupArtifactPath"))
    rehearsal_path = _resolve_existing_path(evidence.get("rehearsalArtifactPath"))
    if source_path is None or backup_path is None or rehearsal_path is None:
        return _refused("Evidence bundle references a missing source, backup, or rehearsal artifact.", "missing_artifact")
    if len({source_path, backup_path, rehearsal_path}) != 3:
        return _refused("Source, backup, and rehearsal artifact paths must be distinct.", "path_aliasing")

    rehearsal_json = evidence.get("rehearsalJson")
    if not isinstance(rehearsal_json, Mapping):
        return _refused("Evidence bundle rehearsalJson must be structured JSON.", "invalid_rehearsal_json")
    missing_rehearsal_field = [field for field in REQUIRED_REHEARSAL_JSON_FIELDS if field not in rehearsal_json]
    if missing_rehearsal_field:
        return _refused(
            f"Rehearsal JSON missing required field: {missing_rehearsal_field[0]}",
            "missing_rehearsal_json_field",
        )
    if not _migration_rows_include_schema_migrations(rehearsal_json.get("postMigrationRows")):
        return _refused("Rehearsal JSON does not include expected schema_migrations evidence.", "missing_schema_migrations")
    if not _counts_are_consistent(rehearsal_json):
        return _refused("Pre/post migration counts are inconsistent for this dry-run boundary.", "count_mismatch")
    note = evidence.get("operatorEscalationNote")
    if not isinstance(note, str) or not any(marker in note.lower() for marker in ("not", "no ")):
        return _refused("Operator escalation note must state which action was intentionally not taken.", "missing_escalation_note")

    validated_artifacts = {
        "sourceDatabasePath": str(source_path),
        "backupArtifactPath": str(backup_path),
        "rehearsalArtifactPath": str(rehearsal_path),
    }
    observed_counts = {
        "preMigrationCounts": rehearsal_json["preMigrationCounts"],
        "postMigrationCounts": rehearsal_json["postMigrationCounts"],
    }
    observed_migration_rows = rehearsal_json["postMigrationRows"]
    observed_readback_post_ids = rehearsal_json["readbackPostIds"]

    if evidence.get("observedStopCondition") == "migration_name_mismatch":
        return {
            "status": "needs_manual_intervention",
            "reason": "migration_name_mismatch requires manual intervention before any repair action.",
            "policyCode": "migration_name_mismatch",
            "validatedArtifacts": validated_artifacts,
            "observedCounts": observed_counts,
            "observedMigrationRows": observed_migration_rows,
            "observedReadbackPostIds": observed_readback_post_ids,
            "recommendedNextAction": "Escalate with the evidence bundle; do not edit schema_migrations.",
        }

    return {
        "status": "analysis_ready",
        "reason": "Evidence bundle passed dry-run preflight checks.",
        "policyCode": None,
        "validatedArtifacts": validated_artifacts,
        "observedCounts": observed_counts,
        "observedMigrationRows": observed_migration_rows,
        "observedReadbackPostIds": observed_readback_post_ids,
        "recommendedNextAction": "Keep artifacts for review; do not run repair commands from this dry-run analysis.",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run analyze a PostStore migration repair evidence bundle.")
    parser.add_argument("--evidence", required=True, type=Path, help="Evidence bundle JSON file to analyze.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        raw_evidence = json.loads(args.evidence.read_text())
    except (OSError, json.JSONDecodeError) as error:
        print(
            json.dumps(
                _refused(f"Could not read evidence bundle: {error}", "unreadable_evidence_bundle"),
                sort_keys=True,
            )
        )
        return 2
    if not isinstance(raw_evidence, Mapping):
        print(json.dumps(_refused("Evidence bundle must be a JSON object.", "invalid_evidence_bundle"), sort_keys=True))
        return 2

    result = analyze_evidence_bundle(raw_evidence)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in {"analysis_ready", "needs_manual_intervention"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
