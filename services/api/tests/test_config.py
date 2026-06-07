import pytest
from pydantic import ValidationError

from nairi_api.config import Settings


def test_public_invalidation_dispatcher_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", raising=False)

    settings = Settings()

    assert settings.public_invalidation_dispatcher == "none"


def test_public_invalidation_dispatcher_accepts_explicit_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", raising=False)

    settings = Settings(public_invalidation_dispatcher="none")

    assert settings.public_invalidation_dispatcher == "none"


def test_public_invalidation_dispatcher_accepts_contract_adapter_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", raising=False)

    settings = Settings(public_invalidation_dispatcher="contract")

    assert settings.public_invalidation_dispatcher == "contract"


def test_public_invalidation_dispatcher_accepts_cloudflare_adapter_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", raising=False)

    settings = Settings(public_invalidation_dispatcher="cloudflare")

    assert settings.public_invalidation_dispatcher == "cloudflare"


def test_public_invalidation_dispatcher_rejects_unsupported_values() -> None:
    with pytest.raises(ValidationError):
        Settings(public_invalidation_dispatcher="webhook")


def test_public_invalidation_dispatcher_reads_env_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", "none")

    settings = Settings()

    assert settings.public_invalidation_dispatcher == "none"


def test_public_invalidation_dispatcher_reads_env_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", "contract")

    settings = Settings()

    assert settings.public_invalidation_dispatcher == "contract"


def test_public_invalidation_dispatcher_reads_env_cloudflare(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", "cloudflare")

    settings = Settings()

    assert settings.public_invalidation_dispatcher == "cloudflare"


def test_public_invalidation_dispatcher_rejects_unsupported_env_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", "webhook")

    with pytest.raises(ValidationError):
        Settings()
