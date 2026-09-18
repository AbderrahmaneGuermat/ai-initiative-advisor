"""Execution limits for one advisory turn.

These exist so that an adaptive loop terminates. The next-action prompt decides
what happens next, which means nothing in a prompt file can be trusted to stop
the loop, and nothing in a prompt file is asked to.

Every limit is counted here, in code, where no prompt can widen it.

The request budget counts **every** call to the provider, including the
next-action selector and any repair attempt. Excluding them would make the
budget a fiction: a turn could issue three selector calls, three actions and
three repairs while reporting three requests.

The wall-clock budget is a **deadline**, not a between-steps check. An earlier
version tested elapsed time only between loop iterations, so a single slow
request could run well past the limit and still commit its output. The deadline
is now applied around each awaited call and re-checked before anything is
written, so a turn that overruns is cancelled rather than merely noticed
afterwards.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


class LimitExceeded(RuntimeError):
    """A turn hit a ceiling and was stopped.

    Not a defect. It is the limit doing its job, and it is reported to the
    manager as the advisor stopping rather than as a crash.
    """

    def __init__(self, limit_name: str, detail: str) -> None:
        super().__init__(detail)
        self.limit_name = limit_name
        self.detail = detail


@dataclass(frozen=True)
class Limits:
    """Ceilings for a single turn."""

    #: Actions the loop may execute in one turn, selector calls excluded.
    max_actions: int = 4
    #: Provider requests per turn, selector and repair calls included.
    max_model_requests: int = 8
    #: Repair attempts per invalid output. One, and only one.
    max_repairs_per_output: int = 1
    #: Characters of assembled input per request. A cheap guard against an
    #: oversized brief becoming an expensive call.
    max_input_chars: int = 60_000
    #: Wall-clock seconds for the whole turn, enforced as a deadline.
    #: Configurable through MAX_TURN_SECONDS; see app.config.
    max_turn_seconds: float = 300.0

    #: Clarification rounds the advisor may open per session.
    #:
    #: One by default. After the manager has answered a round, the advisor
    #: proceeds with what it has and records the rest as open unknowns, rather
    #: than opening another round. The first live run asked six questions across
    #: two rounds before comparing anything, which is more interrogation than a
    #: manager will sit through.
    max_clarification_rounds: int = 1


def limits_from_settings() -> "Limits":
    """Build limits from configuration.

    Only the turn deadline is configurable. The rest are engineering judgements
    that a deployment has no business loosening.
    """
    from app.config import settings

    return Limits(max_turn_seconds=settings.max_turn_seconds)


@dataclass
class TurnBudget:
    """What a turn has spent so far.

    Mutable and short-lived: one instance per turn, discarded when it ends.
    """

    limits: Limits = field(default_factory=Limits)
    actions_taken: int = 0
    model_requests: int = 0
    started_at: float | None = None
    elapsed_seconds: float = 0.0

    # --- Time -------------------------------------------------------------

    def start(self) -> None:
        self.started_at = time.monotonic()

    def elapsed(self) -> float:
        if self.started_at is None:
            return 0.0
        self.elapsed_seconds = time.monotonic() - self.started_at
        return self.elapsed_seconds

    def remaining(self) -> float:
        """Seconds left before the deadline. May be zero or negative."""
        return self.limits.max_turn_seconds - self.elapsed()

    def require_time(self, what: str) -> float:
        """Seconds available for ``what``, or raise if the deadline has passed.

        Called immediately before an awaited call, to bound it, and immediately
        after, to stop a result that arrived too late from being committed.
        """
        left = self.remaining()
        if left <= 0:
            raise LimitExceeded(
                "max_turn_seconds",
                f"the turn deadline of {self.limits.max_turn_seconds:.0f}s passed "
                f"during {what} (elapsed {self.elapsed_seconds:.1f}s)",
            )
        return left

    def expired(self, what: str) -> LimitExceeded:
        """The error to raise when an awaited call was cancelled by the deadline."""
        return LimitExceeded(
            "max_turn_seconds",
            f"{what} was cancelled after the turn deadline of "
            f"{self.limits.max_turn_seconds:.0f}s (elapsed {self.elapsed():.1f}s)",
        )

    # --- Countable resources ---------------------------------------------

    def check_input_size(self, text: str) -> None:
        if len(text) > self.limits.max_input_chars:
            raise LimitExceeded(
                "max_input_chars",
                f"assembled input is {len(text)} characters, over the "
                f"{self.limits.max_input_chars} limit",
            )

    def charge_model_request(self) -> None:
        """Count one provider request. Selector, action and repair alike."""
        if self.model_requests >= self.limits.max_model_requests:
            raise LimitExceeded(
                "max_model_requests",
                f"this turn has already made {self.model_requests} model requests",
            )
        self.model_requests += 1

    def charge_action(self) -> None:
        if self.actions_taken >= self.limits.max_actions:
            raise LimitExceeded(
                "max_actions",
                f"this turn has already executed {self.actions_taken} actions",
            )
        self.actions_taken += 1

    def summary(self) -> dict[str, float | int]:
        return {
            "actions_taken": self.actions_taken,
            "model_requests": self.model_requests,
            "elapsed_seconds": round(self.elapsed(), 2),
            "max_actions": self.limits.max_actions,
            "max_model_requests": self.limits.max_model_requests,
            "max_turn_seconds": self.limits.max_turn_seconds,
        }
