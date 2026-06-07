import pytest
from pydantic import ValidationError

from nairi_api.config import Settings


def test_public_invalidation_dispatcher_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", raising=False)

    settings = Settings()

    assert settings.public_invalidation_dispatcher == "none"


def test_cloudflare_invalidation_settings_default_to_unconfigured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID", raising=False)
    monkeypatch.delenv("NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN", raising=False)

    settings = Settings()

    assert settings.public_invalidation_cloudflare_zone_id is None
    assert settings.public_invalidation_cloudflare_api_token is None


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


def test_cloudflare_invalidation_settings_read_env_without_printing_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID", "zone-test")
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN", "token-test")

    settings = Settings()

    assert settings.public_invalidation_cloudflare_zone_id == "zone-test"
    assert settings.public_invalidation_cloudflare_api_token.get_secret_value() == "token-test"
    assert "token-test" not in repr(settings)


def test_public_invalidation_dispatcher_rejects_unsupported_env_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIRI_PUBLIC_INVALIDATION_DISPATCHER", "webhook")

    with pytest.raises(ValidationError):
        Settings()
