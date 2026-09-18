"""Deterministic test doubles.

No test in this suite touches the network or needs an API key.

The double implements the same narrow protocol the advisory loop depends on and
records every call, so a test can assert on **what was actually sent** rather
than inferring it from what came back. That distinction matters for the prompt
reload test: two different answers would not prove a prompt changed, but the
instructions passed to the adapter do.

These doubles live under ``tests/`` and are never importable from application
code, so there is no path by which a scripted response could reach a manager
presented as live model output.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.core.model_client import ModelCall
from app.models import wire as w


@dataclass
class RecordedCall:
    instructions: str
    input_text: str
    schema: type[BaseModel]
    schema_name: str


@dataclass
class Delayed:
    """A queued response that takes time to arrive.

    Used to test the turn deadline and the session lock, both of which only
    matter while a call is in flight.
    """

    payload: Any
    seconds: float


class ScriptedClient:
    """Returns queued responses in order, recording every request.

    A queued item that is an exception is raised instead of returned, which is
    how provider failures are simulated.
    """

    def __init__(self, responses: list[Any] | None = None) -> None:
        self.responses: list[Any] = list(responses or [])
        self.calls: list[RecordedCall] = []
        #: Optional hook invoked inside each call, for observing state while a
        #: request is in flight.
        self.on_call: Any = None

    @property
    def model_name(self) -> str:
        return "scripted-test-double"

    def queue(self, *items: Any) -> None:
        self.responses.extend(items)

    async def complete(
        self,
        *,
        instructions: str,
        input_text: str,
        schema: type[BaseModel],
        schema_name: str,
    ) -> ModelCall:
        self.calls.append(
            RecordedCall(
                instructions=instructions,
                input_text=input_text,
                schema=schema,
                schema_name=schema_name,
            )
        )

        if not self.responses:
            raise AssertionError(
                f"the double ran out of scripted responses; the loop asked for {schema_name}"
            )

        item = self.responses.pop(0)

        if isinstance(item, Delayed):
            # Sleeps inside the awaited call, exactly where a real request
            # would. asyncio.wait_for can therefore cancel it.
            await asyncio.sleep(item.seconds)
            item = item.payload

        if self.on_call is not None:
            self.on_call(len(self.calls))

        if isinstance(item, Exception):
            raise item

        return ModelCall(
            parsed=item,
            model=self.model_name,
            input_tokens=100,
            output_tokens=200,
            total_tokens=300,
            duration_ms=1,
            response_id="resp_double",
        )


# --- Wire payload builders -----------------------------------------------
#
# Written out rather than generated, so a test reads as the exchange it is
# describing.


def next_action(action: str, reasoning: str = "scripted choice") -> w.WireNextAction:
    return w.WireNextAction(action=action, reasoning=reasoning)


def diagnosis(context_id: str = "CTX-LARKFIELD-1") -> w.WireDiagnosis:
    return w.WireDiagnosis(
        context_id=context_id,
        gaps=[
            w.WireGap(
                description="The headcount constraint has no value.",
                why_it_matters="Every option needs an owner after launch.",
                relates_to=[w.WireSourceRef(kind="brief.constraint", ref_id="CON-TEAM")],
            )
        ],
        contradictions=[],
        unstated_assumptions=[],
        summary="Workable but thin. Ownership is the largest gap.",
    )


def clarification(ids: list[str] | None = None) -> w.WireClarificationBatch:
    ids = ids or ["Q-VOLUME", "Q-DATA", "Q-TEAM"]
    return w.WireClarificationBatch(
        questions=[
            w.WireClarificationQuestion(
                id=qid,
                question=f"Scripted question {qid}?",
                why_it_matters="It would change which option comes first.",
                relates_to=[],
            )
            for qid in ids
        ]
    )


def _claim(statement: str, sources: list[tuple[str, str]] | None = None) -> w.WireClaim:
    return w.WireClaim(
        statement=statement,
        sources=[w.WireSourceRef(kind=k, ref_id=r) for k, r in (sources or [])],
    )


def comparison(
    context_id: str = "CTX-LARKFIELD-1",
    initiative_ids: list[str] | None = None,
) -> w.WireComparison:
    initiative_ids = initiative_ids or ["INI-ROUTE", "INI-DOCS", "INI-CHAT"]
    return w.WireComparison(
        context_id=context_id,
        criteria_considered=["Time to a demonstrable result", "Dependence on existing data"],
        initiatives=[
            w.WireInitiativeComparison(
                initiative_id=iid,
                stated_facts=[
                    _claim(
                        "The manager listed this option.",
                        [("brief.initiative", iid)],
                    )
                ],
                assumptions=[_claim("Assumed, and nobody has checked it.")],
                missing_evidence=[
                    w.WireMissingEvidence(
                        description="What this would cost.",
                        why_it_matters="The budget is known and the cost is not.",
                        how_it_could_be_resolved="Ask for two vendor quotes.",
                    )
                ],
                feasibility_constraints=[
                    _claim(
                        "Address data must stay in the EU.",
                        [("brief.constraint", "CON-DATA")],
                    )
                ],
                trade_offs=[],
            )
            for iid in initiative_ids
        ],
        cross_cutting_notes=[],
    )


def recommendation(
    context_id: str = "CTX-LARKFIELD-1",
    initiative_ids: list[str] | None = None,
    open_unknowns: list[str] | None = None,
) -> w.WireRecommendation:
    initiative_ids = initiative_ids or ["INI-DOCS", "INI-ROUTE", "INI-CHAT"]
    return w.WireRecommendation(
        context_id=context_id,
        summary="Start with the narrowest option.",
        items=[
            w.WireRecommendedItem(
                initiative_id=iid,
                stance="recommended" if index == 0 else "consider_later",
                rationale="Scripted rationale.",
                supported_by=[w.WireSourceRef(kind="brief.initiative", ref_id=iid)],
                rests_on_assumptions=[],
            )
            for index, iid in enumerate(initiative_ids)
        ],
        risks=[
            w.WireRisk(
                description="Nobody owns it after launch.",
                consequence_if_realised="It degrades quietly.",
                early_signal=None,
            )
        ],
        first_actions=[
            w.WireFirstAction(
                action="Sample fifty documents.",
                purpose="Establish a baseline.",
                resolves_unknown="The current error rate.",
            )
        ],
        open_unknowns=open_unknowns if open_unknowns is not None else ["Cost of every option."],
        confidence_note="Moderate on the first step, low on the ordering.",
    )


def context_request() -> w.WireContextRequest:
    return w.WireContextRequest(
        missing=[
            w.WireMissingInput(
                field="What you are trying to achieve",
                why_required="Nothing can be compared without an objective.",
            )
        ],
        message="There is not enough here to begin.",
    )
