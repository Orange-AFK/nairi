from nairi_api.config import Settings
from nairi_api.invalidation_dispatch import (
    ContractPublicInvalidationDispatcher,
    NoopPublicInvalidationDispatcher,
    PublicInvalidationDispatchResult,
    build_public_invalidation_dispatcher,
)
from nairi_api.main import create_app


def test_noop_dispatcher_returns_skipped_without_attempting_external_invalidation() -> None:
    dispatcher = NoopPublicInvalidationDispatcher()

    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="no_dispatcher_configured",
        attempted=False,
        attempted_at=None,
    )


def test_contract_dispatcher_records_contract_only_attempt_without_external_invalidation() -> None:
    dispatcher = ContractPublicInvalidationDispatcher()

    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="contract_only_adapter",
        attempted=True,
        attempted_at="2026-06-07T08:11:12Z",
    )


def test_dispatcher_factory_builds_noop_dispatcher_for_none_configuration() -> None:
    dispatcher = build_public_invalidation_dispatcher(Settings(public_invalidation_dispatcher="none"))

    assert isinstance(dispatcher, NoopPublicInvalidationDispatcher)


def test_dispatcher_factory_builds_contract_dispatcher_for_contract_configuration() -> None:
    dispatcher = build_public_invalidation_dispatcher(Settings(public_invalidation_dispatcher="contract"))

    assert isinstance(dispatcher, ContractPublicInvalidationDispatcher)


def test_create_app_exposes_configured_public_invalidation_dispatcher() -> None:
    app = create_app(settings=Settings(public_invalidation_dispatcher="none"))

    assert isinstance(app.state.public_invalidation_dispatcher, NoopPublicInvalidationDispatcher)


def test_create_app_exposes_contract_public_invalidation_dispatcher() -> None:
    app = create_app(settings=Settings(public_invalidation_dispatcher="contract"))

    assert isinstance(app.state.public_invalidation_dispatcher, ContractPublicInvalidationDispatcher)
