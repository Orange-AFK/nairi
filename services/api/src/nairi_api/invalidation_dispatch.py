from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from nairi_api.config import Settings


@dataclass(frozen=True)
class PublicInvalidationDispatchResult:
    status: Literal["dispatch_skipped", "dispatch_failed"]
    reason: Literal["no_dispatcher_configured", "dispatcher_exception"]
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


def build_public_invalidation_dispatcher(settings: Settings) -> PublicInvalidationDispatcher:
    if settings.public_invalidation_dispatcher == "none":
        return NoopPublicInvalidationDispatcher()
    raise ValueError(f"Unsupported public invalidation dispatcher: {settings.public_invalidation_dispatcher}")
