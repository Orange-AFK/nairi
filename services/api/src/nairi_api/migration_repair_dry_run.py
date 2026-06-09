import argparse
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REQUIRED_EVIDENCE_FIELDS: tuple[str, ...] = (
    "commandInvocation",
    "sourceDatabasePath",
    "backupArtifactPath",
    "rehearsalArtifactPath",
    "stdout",
    "stderr",
    "rehearsalJson",
    "observedStopCondition",
    "operatorEscalationNote",
)

REQUIRED_REHEARSAL_JSON_FIELDS: tuple[str, ...] = (
    "backupPath",
    "rehearsalPath",
    "preMigrationCounts",
    "postMigrationCounts",
    "postMigrationRows",
    "readbackPostIds",
)

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"__[A-Z_]{3,}__"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{10,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[opusr]_[A-Za-z0-9_]{20,}"),
)

_ESCALATION_KEYWORDS: tuple[str, ...] = (
    "No metadata",
    "production mutation",
    "live database",
    "metadata edit",
)


def _check_evidence_fields(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if a required field is missing, else None."""
    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in evidence:
            return "missing_evidence_field"
    return None


def _check_artifacts_exist(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if any artifact path does not exist, else None."""
    for key in ("sourceDatabasePath", "backupArtifactPath", "rehearsalArtifactPath"):
        path = evidence[key]
        if isinstance(path, str) and not Path(path).exists():
            return "missing_artifact"
    return None


def _check_path_aliasing(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if any two artifact paths resolve to the same location, else None."""
    paths = [
        str(Path(evidence["sourceDatabasePath"]).resolve()),
        str(Path(evidence["backupArtifactPath"]).resolve()),
        str(Path(evidence["rehearsalArtifactPath"]).resolve()),
    ]
    if len(paths) != len(set(paths)):
        return "path_aliasing"
    return None


def _check_rehearsal_json_is_dict(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if rehearsalJson is not a dict, else None."""
    rj = evidence.get("rehearsalJson")
    if not isinstance(rj, dict):
        return "invalid_rehearsal_json"
    return None


def _check_rehearsal_json_fields(rehearsal_json: Mapping[str, Any]) -> str | None:
    """Return policyCode if a required rehearsal JSON field is missing, else None."""
    for field in REQUIRED_REHEARSAL_JSON_FIELDS:
        if field not in rehearsal_json:
            return "missing_rehearsal_json_field"
    return None


def _check_schema_migrations_present(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if stop_condition is migration_name_mismatch but postMigrationRows is empty."""
    stop_condition = evidence.get("observedStopCondition")
    if stop_condition == "migration_name_mismatch":
        rj = evidence.get("rehearsalJson")
        if isinstance(rj, dict):
            rows = rj.get("postMigrationRows")
            if isinstance(rows, list) and len(rows) == 0:
                return "missing_schema_migrations"
    return None


def _check_counts_match(rehearsal_json: Mapping[str, Any]) -> str | None:
    """Return policyCode if preMigrationCounts != postMigrationCounts, else None."""
    pre = rehearsal_json.get("preMigrationCounts")
    post = rehearsal_json.get("postMigrationCounts")
    if isinstance(pre, dict) and isinstance(post, dict):
        if pre != post:
            return "count_mismatch"
    return None


def _check_escalation_note(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if operatorEscalationNote lacks required detail, else None."""
    note = evidence.get("operatorEscalationNote", "")
    if not isinstance(note, str):
        return "missing_escalation_note"
    if not any(keyword.lower() in note.lower() for keyword in _ESCALATION_KEYWORDS):
        return "missing_escalation_note"
    return None


def _has_secret_like_text(value: object) -> bool:
    """Check if a string value contains secret-like patterns."""
    if not isinstance(value, str):
        return False
    for pattern in _SECRET_PATTERNS:
        if pattern.search(value):
            return True
    return False


def _check_secret_like_evidence(evidence: Mapping[str, Any]) -> str | None:
    """Return policyCode if any evidence field contains secret-like text, else None."""
    for key, value in evidence.items():
        if _has_secret_like_text(value):
            return "secret_like_evidence"
        if isinstance(value, (dict, list)):
            stack: list[object] = [value]
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    for v in item.values():
                        if _has_secret_like_text(v):
                            return "secret_like_evidence"
                        if isinstance(v, (dict, list)):
                            stack.append(v)
                elif isinstance(item, list):
                    for elem in item:
                        if _has_secret_like_text(elem):
                            return "secret_like_evidence"
                        if isinstance(elem, (dict, list)):
                            stack.append(elem)
    return None


def _build_refused(policy_code: str, reason: str) -> dict[str, object]:
    return {
        "status": "refused",
        "reason": reason,
        "policyCode": policy_code,
        "validatedArtifacts": None,
        "observedCounts": None,
        "observedMigrationRows": None,
        "observedReadbackPostIds": None,
        "recommendedNextAction": None,
    }


def _build_intervention(
    evidence: Mapping[str, Any],
    rehearsal_json: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "status": "needs_manual_intervention",
        "reason": "manual intervention is required: the rehearsal detected a migration name mismatch.",
        "policyCode": "migration_name_mismatch",
        "validatedArtifacts": {
            "sourceDatabasePath": evidence["sourceDatabasePath"],
            "backupArtifactPath": evidence["backupArtifactPath"],
            "rehearsalArtifactPath": evidence["rehearsalArtifactPath"],
        },
        "observedCounts": {
            "preMigrationCounts": rehearsal_json["preMigrationCounts"],
            "postMigrationCounts": rehearsal_json["postMigrationCounts"],
        },
        "observedMigrationRows": rehearsal_json.get("postMigrationRows", []),
        "observedReadbackPostIds": rehearsal_json.get("readbackPostIds", []),
        "recommendedNextAction": "Escalate with the evidence bundle; do not edit schema_migrations.",
    }


def _build_analysis_ready(
    evidence: Mapping[str, Any],
    rehearsal_json: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "status": "analysis_ready",
        "reason": "Evidence bundle passed dry-run preflight checks.",
        "policyCode": None,
        "validatedArtifacts": {
            "sourceDatabasePath": evidence["sourceDatabasePath"],
            "backupArtifactPath": evidence["backupArtifactPath"],
            "rehearsalArtifactPath": evidence["rehearsalArtifactPath"],
        },
        "observedCounts": {
            "preMigrationCounts": rehearsal_json["preMigrationCounts"],
            "postMigrationCounts": rehearsal_json["postMigrationCounts"],
        },
        "observedMigrationRows": rehearsal_json.get("postMigrationRows", []),
        "observedReadbackPostIds": rehearsal_json.get("readbackPostIds", []),
        "recommendedNextAction": "Keep artifacts for review; do not run repair commands from this dry-run analysis.",
    }


def analyze_evidence_bundle(evidence: Mapping[str, Any]) -> dict[str, object]:
    """Run dry-run preflight analysis on an evidence bundle.

    Returns the output contract dict as defined in
    memory-bank/executable-repair-tooling.md.
    """
    # --- Preflight checks (fail-fast) ---

    if policy_code := _check_evidence_fields(evidence):
        missing = [f for f in REQUIRED_EVIDENCE_FIELDS if f not in evidence]
        return _build_refused(
            policy_code,
            f"Required evidence field(s) missing: {', '.join(missing)}.",
        )

    if policy_code := _check_artifacts_exist(evidence):
        missing = []
        for key in ("sourceDatabasePath", "backupArtifactPath", "rehearsalArtifactPath"):
            path = evidence[key]
            if isinstance(path, str) and not Path(path).exists():
                missing.append(key)
        return _build_refused(
            policy_code,
            f"Required artifact(s) do not exist: {', '.join(missing)}.",
        )

    if policy_code := _check_path_aliasing(evidence):
        return _build_refused(
            policy_code,
            "Two or more artifact paths resolve to the same location.",
        )

    if policy_code := _check_rehearsal_json_is_dict(evidence):
        return _build_refused(
            policy_code,
            "rehearsalJson is not a structured JSON object.",
        )

    rehearsal_json: Mapping[str, Any] = evidence["rehearsalJson"]  # type: ignore[assignment]

    if policy_code := _check_rehearsal_json_fields(rehearsal_json):
        missing = [f for f in REQUIRED_REHEARSAL_JSON_FIELDS if f not in rehearsal_json]
        return _build_refused(
            policy_code,
            f"Required rehearsal JSON field(s) missing: {', '.join(missing)}.",
        )

    if policy_code := _check_schema_migrations_present(evidence):
        return _build_refused(
            policy_code,
            "Schema migrations metadata is missing from the rehearsal results for a migration-name-mismatch stop condition.",
        )

    if policy_code := _check_counts_match(rehearsal_json):
        return _build_refused(
            policy_code,
            "preMigrationCounts and postMigrationCounts are not equal.",
        )

    if policy_code := _check_escalation_note(evidence):
        return _build_refused(
            policy_code,
            "operatorEscalationNote does not confirm that no metadata edits, production mutation, or live database migration execution were performed.",
        )

    if policy_code := _check_secret_like_evidence(evidence):
        return _build_refused(
            policy_code,
            "Evidence bundle contains secret-like text in one or more fields.",
        )

    # --- Decision logic ---

    stop_condition = evidence.get("observedStopCondition")
    if stop_condition == "migration_name_mismatch":
        return _build_intervention(evidence, rehearsal_json)

    return _build_analysis_ready(evidence, rehearsal_json)


def _find_evidence_file_path(argv: Sequence[str] | None) -> str:
    parser = argparse.ArgumentParser(description="Nairi post-store repair dry-run analysis.")
    parser.add_argument("--evidence", required=True, type=str, help="Path to evidence bundle JSON file.")
    args = parser.parse_args(argv)
    return args.evidence


def main(argv: Sequence[str] | None = None) -> int:
    evidence_path_str = _find_evidence_file_path(argv)
    evidence_path = Path(evidence_path_str)

    if not evidence_path.exists() or not evidence_path.is_file():
        payload = _build_refused(
            "unreadable_evidence_bundle",
            f"Cannot read evidence bundle: {evidence_path}",
        )
        print(json.dumps(payload, sort_keys=True))
        return 2

    try:
        raw = evidence_path.read_text()
        evidence = json.loads(raw)
    except (json.JSONDecodeError, OSError):
        payload = _build_refused(
            "invalid_evidence_bundle",
            "Evidence bundle is not valid JSON or cannot be decoded.",
        )
        print(json.dumps(payload, sort_keys=True))
        return 2

    if not isinstance(evidence, dict):
        payload = _build_refused(
            "invalid_evidence_bundle",
            "Evidence bundle is not a JSON object.",
        )
        print(json.dumps(payload, sort_keys=True))
        return 2

    result = analyze_evidence_bundle(evidence)
    print(json.dumps(result, sort_keys=True))

    if result["status"] == "analysis_ready":
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
