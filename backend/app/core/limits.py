"""Execution limits for one advisory turn.

These exist so that an adaptive loop terminates. The next-action prompt decides
what happens next, which means nothing in a prompt file can be trusted to stop
the loop, and nothing in a prompt file is asked to.

Every limit is counted here, in code, where no prompt can widen it.

The request budget counts **every** call to the provider, including the
next-action selector and any repair attempt. Excluding them would make the
budget a fiction: a turn could issue three selector calls, three actions and
three repairs while reporting three requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class LimitExceeded(RuntimeError):
    """A turn hit a ceiling and was stopped.

    Not an error in the sense of a defect. It is the limit doing its job, and it
    is reported to the manager as the advisor stopping rather than as a crash.
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
    #: Wall-clock seconds for the whole turn.
    max_turn_seconds: float = 180.0


@dataclass
class TurnBudget:
    """What a turn has spent so far.

    Mutable and short-lived: one instance per turn, discarded when it ends.
    """

    limits: Limits = field(default_factory=Limits)
    actions_taken: int = 0
    model_requests: int = 0
    elapsed_seconds: float = 0.0

    def check_input_size(self, text: str) -> None:
        if len(text) > self.limits.max_input_chars:
            raise LimitExceeded(
                "max_input_chars",
                f"assembled input is {len(text)} characters, over the "
                f"{self.limits.max_input_chars} limit",
            )

    def charge_model_request(self) -> None:
        """Count one provider request. Called for selector, action and repair alike."""
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

    def check_time(self, elapsed: float) -> None:
        self.elapsed_seconds = elapsed
        if elapsed > self.limits.max_turn_seconds:
            raise LimitExceeded(
                "max_turn_seconds",
                f"this turn has run for {elapsed:.1f}s, over the "
                f"{self.limits.max_turn_seconds:.0f}s limit",
            )

    def summary(self) -> dict[str, float | int]:
        return {
            "actions_taken": self.actions_taken,
            "model_requests": self.model_requests,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "max_actions": self.limits.max_actions,
            "max_model_requests": self.limits.max_model_requests,
        }
