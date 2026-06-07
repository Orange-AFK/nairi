from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from nairi_api.config import Settings


@dataclass(frozen=True)
class PublicInvalidationDispatchResult:
    status: Literal["dispatch_skipped", "dispatch_failed"]
    reason: Literal[
        "no_dispatcher_configured",
        "dispatcher_exception",
        "contract_only_adapter",
        "cloudflare_adapter_disabled",
        "cloudflare_adapter_missing_settings",
    ]
    attempted: bool
    attempted_at: str | None


class PublicInvalidationDispatcher(Protocol):
    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        """Return dispatch bookkeeping for public invalidation surfaces."""


class NoopPublicInvalidationDispatcher:
    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        return PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason="no_dispatcher_configured",
            attempted=False,
            attempted_at=None,
        )


class ContractPublicInvalidationDispatcher:
    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        return PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason="contract_only_adapter",
            attempted=True,
            attempted_at=published_at,
        )


class CloudflarePublicInvalidationDispatcher:
    def __init__(self, *, zone_id: str | None = None, api_token_configured: bool = False) -> None:
        self._zone_id = zone_id
        self._api_token_configured = api_token_configured

    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        reason: Literal["cloudflare_adapter_disabled", "cloudflare_adapter_missing_settings"] = (
            "cloudflare_adapter_disabled"
            if self._zone_id and self._api_token_configured
            else "cloudflare_adapter_missing_settings"
        )
        return PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason=reason,
            attempted=False,
            attempted_at=None,
        )


def build_public_invalidation_dispatcher(settings: Settings) -> PublicInvalidationDispatcher:
    if settings.public_invalidation_dispatcher == "none":
        return NoopPublicInvalidationDispatcher()
    if settings.public_invalidation_dispatcher == "contract":
        return ContractPublicInvalidationDispatcher()
    if settings.public_invalidation_dispatcher == "cloudflare":
        return CloudflarePublicInvalidationDispatcher(
            zone_id=settings.public_invalidation_cloudflare_zone_id,
            api_token_configured=bool(
                settings.public_invalidation_cloudflare_api_token
                and settings.public_invalidation_cloudflare_api_token.get_secret_value()
            ),
        )
    raise ValueError(f"Unsupported public invalidation dispatcher: {settings.public_invalidation_dispatcher}")
