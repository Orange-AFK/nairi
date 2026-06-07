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
    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        return PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason="cloudflare_adapter_disabled",
            attempted=False,
            attempted_at=None,
        )


def build_public_invalidation_dispatcher(settings: Settings) -> PublicInvalidationDispatcher:
    if settings.public_invalidation_dispatcher == "none":
        return NoopPublicInvalidationDispatcher()
    if settings.public_invalidation_dispatcher == "contract":
        return ContractPublicInvalidationDispatcher()
    if settings.public_invalidation_dispatcher == "cloudflare":
        return CloudflarePublicInvalidationDispatcher()
    raise ValueError(f"Unsupported public invalidation dispatcher: {settings.public_invalidation_dispatcher}")
