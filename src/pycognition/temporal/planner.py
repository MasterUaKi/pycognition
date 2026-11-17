# File: src/pycognition/temporal/planner.py
# Version: 1.3.0 | Release Date: 2026-11-17
# EN: Proactive multi-horizon action planner driven by TemporalEventGraph state transitions.
# DE: Proaktiver Multi-Horizont-Aktionsplaner auf Basis von TemporalEventGraph-Zustandsübergängen.

from __future__ import annotations

import hashlib
import inspect
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from pycognition.temporal.graph import StateTransitionEdge, TemporalEventGraph, TransitionType


class PlanningHorizon(str, Enum):
    """
    EN: Temporal planning horizons governing action urgency and orchestration cadence.
    DE: Zeitliche Planungshorizonte für Dringlichkeit und Orchestrierungsrhythmus.
    """
    H1_IMMEDIATE = "H1_IMMEDIATE"    # 0–24 hours: urgent deadline alerts, reopened calls
    H2_TACTICAL = "H2_TACTICAL"      # 1–14 days: targeted verification re-crawls, digest updates
    H3_STRATEGIC = "H3_STRATEGIC"    # 14+ days: archival consolidation, external DMS/CRIS sync


class ActionPriority(IntEnum):
    """
    EN: Execution priority levels (lower integer = higher urgency).
    DE: Ausführungsprioritäten (niedrigere Zahl = höhere Dringlichkeit).
    """
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TriggerPolicy(BaseModel):
    """
    EN: Declarative rule mapping a TemporalEventGraph TransitionType to a proactive action.
    DE: Deklarative Regel zur Zuordnung eines TransitionType zu einer proaktiven Aktion.
    """
    policy_name: str
    trigger_transition: TransitionType
    horizon: PlanningHorizon
    action_type: str
    priority: ActionPriority = ActionPriority.MEDIUM
    cooldown_hours: float = 24.0


class PlannedAction(BaseModel):
    """
    EN: Concrete scheduled action emitted by ProactiveHorizonPlanner.
    DE: Konkrete geplante Aktion des ProactiveHorizonPlanner.
    """
    action_id: str
    horizon: PlanningHorizon
    priority: ActionPriority
    action_type: str
    canonical_id: str
    entity_title: str
    rationale: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed: bool = False


ActionHandlerFn = Callable[[PlannedAction], Awaitable[Any] | Any]


class ProactiveHorizonPlanner:
    """
    EN: Evaluates bitemporal StateTransitionEdges against multi-horizon TriggerPolicies,
        enforces cooldown deduplication, and dispatches prioritized autonomous actions.
    DE: Bewertet bitemporale StateTransitionEdges gegen Multi-Horizont-TriggerPolicies,
        verhindert Duplikate über Cooldowns und führt priorisierte Aktionen aus.
    """

    def __init__(self, policies: Optional[List[TriggerPolicy]] = None) -> None:
        self.policies: List[TriggerPolicy] = policies if policies is not None else self.default_policies()
        self._queue: List[PlannedAction] = []
        self._last_triggered: Dict[str, datetime] = {}
        self._handlers: Dict[str, ActionHandlerFn] = {}

    @staticmethod
    def default_policies() -> List[TriggerPolicy]:
        """
        EN: Built-in multi-horizon policies covering H1 immediate, H2 tactical, and H3 strategic events.
        DE: Standard-Richtlinien für H1-Sofort-, H2-Taktik- und H3-Strategie-Ereignisse.
        """
        return [
            TriggerPolicy(
                policy_name="urgent_deadline_alert",
                trigger_transition=TransitionType.STATUS_EXPIRING_SOON,
                horizon=PlanningHorizon.H1_IMMEDIATE,
                action_type="DISPATCH_URGENT_ALERT",
                priority=ActionPriority.CRITICAL,
                cooldown_hours=72.0,
            ),
            TriggerPolicy(
                policy_name="reopened_program_alert",
                trigger_transition=TransitionType.STATUS_REOPENED,
                horizon=PlanningHorizon.H1_IMMEDIATE,
                action_type="DISPATCH_REOPENED_NOTICE",
                priority=ActionPriority.HIGH,
                cooldown_hours=24.0,
            ),
            TriggerPolicy(
                policy_name="deadline_extension_sync",
                trigger_transition=TransitionType.DEADLINE_EXTENDED,
                horizon=PlanningHorizon.H2_TACTICAL,
                action_type="UPDATE_DEADLINE_RECORD",
                priority=ActionPriority.HIGH,
                cooldown_hours=12.0,
            ),
            TriggerPolicy(
                policy_name="new_entity_enrichment",
                trigger_transition=TransitionType.CREATED,
                horizon=PlanningHorizon.H2_TACTICAL,
                action_type="ENRICH_AND_INDEX_ENTITY",
                priority=ActionPriority.MEDIUM,
                cooldown_hours=24.0,
            ),
            TriggerPolicy(
                policy_name="cross_source_reconciliation",
                trigger_transition=TransitionType.ALIAS_MERGED,
                horizon=PlanningHorizon.H2_TACTICAL,
                action_type="CONSOLIDATE_CROSS_SOURCE_METADATA",
                priority=ActionPriority.MEDIUM,
                cooldown_hours=12.0,
            ),
            TriggerPolicy(
                policy_name="expired_entity_archival",
                trigger_transition=TransitionType.STATUS_EXPIRED,
                horizon=PlanningHorizon.H3_STRATEGIC,
                action_type="ARCHIVE_EXPIRED_ENTITY",
                priority=ActionPriority.LOW,
                cooldown_hours=168.0,
            ),
        ]

    def register_handler(self, action_type: str, handler: ActionHandlerFn) -> None:
        self._handlers[action_type] = handler

    def plan_from_transitions(
        self,
        transitions: List[StateTransitionEdge],
        graph: Optional[TemporalEventGraph] = None,
        now: Optional[datetime] = None,
    ) -> List[PlannedAction]:
        """
        EN: Matches incoming StateTransitionEdges against active TriggerPolicies and
            enqueues deduplicated, priority-sorted PlannedActions.
        DE: Gleiche eingehende StateTransitionEdges mit TriggerPolicies ab und reiht
            deduplizierte, priorisierte PlannedActions in die Warteschlange ein.
        """
        ref_time = now or datetime.now(timezone.utc)
        newly_planned: List[PlannedAction] = []

        for edge in transitions:
            node = graph.get_node(edge.canonical_id) if graph is not None else None
            entity_title = node.primary_title if node is not None else edge.canonical_id

            for policy in self.policies:
                if policy.trigger_transition != edge.transition:
                    continue

                cooldown_key = f"{policy.policy_name}:{edge.canonical_id}"
                last_run = self._last_triggered.get(cooldown_key)
                if last_run is not None and (ref_time - last_run) < timedelta(hours=policy.cooldown_hours):
                    continue

                action_id = hashlib.sha256(
                    f"{cooldown_key}|{edge.edge_id}".encode("utf-8")
                ).hexdigest()[:20]

                action = PlannedAction(
                    action_id=action_id,
                    horizon=policy.horizon,
                    priority=policy.priority,
                    action_type=policy.action_type,
                    canonical_id=edge.canonical_id,
                    entity_title=entity_title,
                    rationale=(
                        f"Policy '{policy.policy_name}' triggered by {edge.transition.value} "
                        f"(source={edge.source_id})."
                    ),
                    payload={
                        "edge_id": edge.edge_id,
                        "from_state": edge.from_state.value if edge.from_state else None,
                        "to_state": edge.to_state.value,
                        "delta": edge.delta,
                        "deadline_iso": node.deadline_iso if node else None,
                    },
                    created_at=ref_time,
                )
                self._last_triggered[cooldown_key] = ref_time
                self._queue.append(action)
                newly_planned.append(action)

        self._queue.sort(key=lambda a: (int(a.priority), a.created_at))
        return newly_planned

    def get_pending_actions(self, horizon: Optional[PlanningHorizon] = None) -> List[PlannedAction]:
        pending = [a for a in self._queue if not a.executed]
        if horizon is not None:
            pending = [a for a in pending if a.horizon == horizon]
        return sorted(pending, key=lambda a: (int(a.priority), a.created_at))

    async def execute_pending(self, horizon: Optional[PlanningHorizon] = None) -> int:
        """
        EN: Executes all pending actions matching the specified horizon using registered handlers.
        DE: Führt alle ausstehenden Aktionen des angegebenen Horizonts über registrierte Handler aus.
        """
        executed_count = 0
        for action in self.get_pending_actions(horizon=horizon):
            handler = self._handlers.get(action.action_type)
            if handler is not None:
                res = handler(action)
                if inspect.isawaitable(res):
                    await res
            action.executed = True
            executed_count += 1
        return executed_count
