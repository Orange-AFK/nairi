import json
import sqlite3
from pathlib import Path

from nairi_api.migration_repair_dry_run import analyze_evidence_bundle, main


def create_sqlite_artifact(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE marker (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO marker (id) VALUES ('unchanged')")


def evidence_bundle(tmp_path: Path, *, stop_condition: str | None = None) -> dict[str, object]:
    source_path = tmp_path / "source.db"
    backup_path = tmp_path / "backup" / "source.db.bak"
    rehearsal_path = tmp_path / "rehearsal" / "working.db"
    for path in (source_path, backup_path, rehearsal_path):
        create_sqlite_artifact(path)
    return {
        "commandInvocation": "nairi-post-store-migration-rehearsal --source source.db --backup backup/source.db.bak --rehearsal rehearsal/working.db",
        "sourceDatabasePath": str(source_path),
        "backupArtifactPath": str(backup_path),
        "rehearsalArtifactPath": str(rehearsal_path),
        "stdout": json.dumps(
            {
                "backupPath": str(backup_path),
                "rehearsalPath": str(rehearsal_path),
                "preMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
                "postMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
                "postMigrationRows": [[1, "post_store_baseline"]],
                "readbackPostIds": ["draft-cli"],
            }
        ),
        "stderr": "",
        "rehearsalJson": {
            "backupPath": str(backup_path),
            "rehearsalPath": str(rehearsal_path),
            "preMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
            "postMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
            "postMigrationRows": [[1, "post_store_baseline"]],
            "readbackPostIds": ["draft-cli"],
        },
        "observedStopCondition": stop_condition,
        "operatorEscalationNote": "No metadata edits, production mutation, or live database migration execution were performed.",
    }


def test_repair_dry_run_cli_has_project_script_entrypoint() -> None:
    import tomllib

    project_config = tomllib.loads(Path("pyproject.toml").read_text())

    assert project_config["project"]["scripts"]["nairi-post-store-repair-dry-run"] == (
        "nairi_api.migration_repair_dry_run:main"
    )


def test_repair_dry_run_analyzes_complete_evidence_without_mutating_artifacts(tmp_path: Path) -> None:
    evidence = evidence_bundle(tmp_path)

    result = analyze_evidence_bundle(evidence)

    assert result == {
        "status": "analysis_ready",
        "reason": "Evidence bundle passed dry-run preflight checks.",
        "policyCode": None,
        "validatedArtifacts": {
            "sourceDatabasePath": str(tmp_path / "source.db"),
            "backupArtifactPath": str(tmp_path / "backup" / "source.db.bak"),
            "rehearsalArtifactPath": str(tmp_path / "rehearsal" / "working.db"),
        },
        "observedCounts": {
            "preMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
            "postMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
        },
        "observedMigrationRows": [[1, "post_store_baseline"]],
        "observedReadbackPostIds": ["draft-cli"],
        "recommendedNextAction": "Keep artifacts for review; do not run repair commands from this dry-run analysis.",
    }
    for path_key in ("sourceDatabasePath", "backupArtifactPath", "rehearsalArtifactPath"):
        with sqlite3.connect(evidence[path_key]) as connection:  # type: ignore[arg-type]
            assert connection.execute("SELECT id FROM marker").fetchall() == [("unchanged",)]


def test_repair_dry_run_maps_migration_name_mismatch_to_manual_intervention(tmp_path: Path) -> None:
    evidence = evidence_bundle(tmp_path, stop_condition="migration_name_mismatch")
    evidence["rehearsalJson"] = {
        **evidence["rehearsalJson"],  # type: ignore[arg-type]
        "postMigrationRows": [[1, "renamed_baseline"]],
    }

    result = analyze_evidence_bundle(evidence)

    assert result["status"] == "needs_manual_intervention"
    assert result["policyCode"] == "migration_name_mismatch"
    assert "manual intervention" in result["reason"]
    assert result["recommendedNextAction"] == "Escalate with the evidence bundle; do not edit schema_migrations."


def test_repair_dry_run_refuses_mismatch_without_schema_migration_evidence(tmp_path: Path) -> None:
    evidence = evidence_bundle(tmp_path, stop_condition="migration_name_mismatch")
    evidence["rehearsalJson"] = {
        **evidence["rehearsalJson"],  # type: ignore[arg-type]
        "postMigrationRows": [],
    }

    result = analyze_evidence_bundle(evidence)

    assert result["status"] == "refused"
    assert result["policyCode"] == "missing_schema_migrations"


def test_repair_dry_run_refuses_missing_required_evidence(tmp_path: Path) -> None:
    evidence = evidence_bundle(tmp_path)
    del evidence["stdout"]

    result = analyze_evidence_bundle(evidence)

    assert result["status"] == "refused"
    assert result["policyCode"] == "missing_evidence_field"
    assert "stdout" in result["reason"]


def test_repair_dry_run_cli_reads_evidence_file_and_outputs_json(tmp_path: Path, capsys) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence_bundle(tmp_path)))

    exit_code = main(["--evidence", str(evidence_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert json.loads(captured.out)["status"] == "analysis_ready"
    assert captured.err == ""


def test_repair_dry_run_cli_fails_closed_for_refused_evidence(tmp_path: Path, capsys) -> None:
    evidence = evidence_bundle(tmp_path)
    evidence["commandInvocation"] = "nairi-post-store-migration-rehearsal --token __SECRET_LIKE__"
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence))

    exit_code = main(["--evidence", str(evidence_path)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert json.loads(captured.out)["status"] == "refused"
    assert captured.err == ""
