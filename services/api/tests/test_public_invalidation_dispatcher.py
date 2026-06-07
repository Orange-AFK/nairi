from nairi_api.config import Settings
from nairi_api.invalidation_dispatch import (
    CloudflarePublicInvalidationDispatcher,
    CloudflarePurgeRequestPlan,
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


def test_cloudflare_dispatcher_records_missing_settings_without_external_invalidation() -> None:
    dispatcher = CloudflarePublicInvalidationDispatcher()

    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="cloudflare_adapter_missing_settings",
        attempted=False,
        attempted_at=None,
    )


def test_cloudflare_factory_records_missing_settings_without_external_invalidation() -> None:
    settings = Settings(public_invalidation_dispatcher="cloudflare")
    dispatcher = build_public_invalidation_dispatcher(settings)

    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="cloudflare_adapter_missing_settings",
        attempted=False,
        attempted_at=None,
    )


def test_cloudflare_factory_keeps_configured_settings_disabled_without_external_invalidation() -> None:
    settings = Settings(
        public_invalidation_dispatcher="cloudflare",
        public_invalidation_cloudflare_zone_id="zone-test",
        public_invalidation_cloudflare_api_token="stub",
    )
    dispatcher = build_public_invalidation_dispatcher(settings)

    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="cloudflare_adapter_dry_run",
        attempted=True,
        attempted_at="2026-06-07T08:11:12Z",
    )


def test_cloudflare_factory_records_missing_settings_for_partial_cloudflare_configuration() -> None:
    partial_settings = [
        Settings(
            public_invalidation_dispatcher="cloudflare",
            public_invalidation_cloudflare_zone_id="zone-test",
        ),
        Settings(
            public_invalidation_dispatcher="cloudflare",
            public_invalidation_cloudflare_api_token="stub",
        ),
        Settings(
            public_invalidation_dispatcher="cloudflare",
            public_invalidation_cloudflare_zone_id="zone-test",
            public_invalidation_cloudflare_api_token="",
        ),
    ]

    for settings in partial_settings:
        dispatcher = build_public_invalidation_dispatcher(settings)
        result = dispatcher.dispatch(surfaces=["/posts"], published_at="2026-06-07T08:11:12Z")

        assert result == PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason="cloudflare_adapter_missing_settings",
            attempted=False,
            attempted_at=None,
        )


def test_cloudflare_dispatcher_builds_purge_request_plan_without_token_or_external_invalidation() -> None:
    dispatcher = CloudflarePublicInvalidationDispatcher(zone_id="zone-test", api_token_configured=True)

    plan = dispatcher.build_purge_request_plan(surfaces=["/posts", "/rss.xml", "/posts"])

    assert plan == CloudflarePurgeRequestPlan(
        method="POST",
        path="/client/v4/zones/zone-test/purge_cache",
        body={"files": ["/posts", "/rss.xml"]},
    )
    assert "stub" not in repr(plan)
    assert "Authorization" not in repr(plan)
    assert "Bearer" not in repr(plan)


def test_cloudflare_dispatcher_does_not_build_purge_request_plan_without_required_settings() -> None:
    dispatcher = CloudflarePublicInvalidationDispatcher(zone_id="zone-test", api_token_configured=False)

    assert dispatcher.build_purge_request_plan(surfaces=["/posts"]) is None


def test_cloudflare_factory_exposes_request_plan_and_records_dry_run_without_external_invalidation() -> None:
    settings = Settings(
        public_invalidation_dispatcher="cloudflare",
        public_invalidation_cloudflare_zone_id="zone-test",
        public_invalidation_cloudflare_api_token="stub",
    )
    dispatcher = build_public_invalidation_dispatcher(settings)

    assert isinstance(dispatcher, CloudflarePublicInvalidationDispatcher)
    assert dispatcher.build_purge_request_plan(surfaces=["/posts"]) == CloudflarePurgeRequestPlan(
        method="POST",
        path="/client/v4/zones/zone-test/purge_cache",
        body={"files": ["/posts"]},
    )
    result = dispatcher.dispatch(surfaces=["/posts", "/rss.xml", "/posts"], published_at="2026-06-07T08:11:12Z")

    assert result == PublicInvalidationDispatchResult(
        status="dispatch_skipped",
        reason="cloudflare_adapter_dry_run",
        attempted=True,
        attempted_at="2026-06-07T08:11:12Z",
    )
    assert "CloudflarePurgeRequestPlan" not in repr(result)
    assert "zone-test" not in repr(result)
    assert "stub" not in repr(result)
    assert "Authorization" not in repr(result)
    assert "Bearer" not in repr(result)


def test_dispatcher_factory_builds_noop_dispatcher_for_none_configuration() -> None:
    dispatcher = build_public_invalidation_dispatcher(Settings(public_invalidation_dispatcher="none"))

    assert isinstance(dispatcher, NoopPublicInvalidationDispatcher)


def test_dispatcher_factory_builds_contract_dispatcher_for_contract_configuration() -> None:
    dispatcher = build_public_invalidation_dispatcher(Settings(public_invalidation_dispatcher="contract"))

    assert isinstance(dispatcher, ContractPublicInvalidationDispatcher)


def test_dispatcher_factory_builds_cloudflare_dispatcher_for_cloudflare_configuration() -> None:
    dispatcher = build_public_invalidation_dispatcher(Settings(public_invalidation_dispatcher="cloudflare"))

    assert isinstance(dispatcher, CloudflarePublicInvalidationDispatcher)


def test_create_app_exposes_configured_public_invalidation_dispatcher() -> None:
    app = create_app(settings=Settings(public_invalidation_dispatcher="none"))

    assert isinstance(app.state.public_invalidation_dispatcher, NoopPublicInvalidationDispatcher)


def test_create_app_exposes_contract_public_invalidation_dispatcher() -> None:
    app = create_app(settings=Settings(public_invalidation_dispatcher="contract"))

    assert isinstance(app.state.public_invalidation_dispatcher, ContractPublicInvalidationDispatcher)


def test_create_app_exposes_cloudflare_public_invalidation_dispatcher() -> None:
    app = create_app(settings=Settings(public_invalidation_dispatcher="cloudflare"))

    assert isinstance(app.state.public_invalidation_dispatcher, CloudflarePublicInvalidationDispatcher)
