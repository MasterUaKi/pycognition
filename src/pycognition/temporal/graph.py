# File: src/pycognition/temporal/graph.py
# Version: 1.3.0 | Release Date: 2026-11-17
# EN: Bitemporal Event Graph for longitudinal entity lifecycle tracking and state-transition auditing.
# DE: Bitemporaler Ereignisgraph zur longitudinalen Verfolgung von Entitätslebenszyklen und Zustandsübergängen.

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class EntityLifecycleState(str, Enum):
    """
    EN: Canonical lifecycle states of a tracked entity across recurring observation cycles.
    DE: Kanonische Lebenszykluszustände einer verfolgten Entität über wiederkehrende Beobachtungszyklen.
    """
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED"
    DEADLINE_EXTENDED = "DEADLINE_EXTENDED"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    REOPENED = "REOPENED"
    ARCHIVED = "ARCHIVED"


class TransitionType(str, Enum):
    """
    EN: Semantic classification of state transitions between consecutive temporal snapshots.
    DE: Semantische Klassifikation von Zustandsübergängen zwischen aufeinanderfolgenden Zeitpunkten.
    """
    CREATED = "CREATED"
    CONFIRMED_UNCHANGED = "CONFIRMED_UNCHANGED"
    ATTRIBUTE_UPDATED = "ATTRIBUTE_UPDATED"
    DEADLINE_EXTENDED = "DEADLINE_EXTENDED"
    DEADLINE_SHORTENED = "DEADLINE_SHORTENED"
    STATUS_EXPIRING_SOON = "STATUS_EXPIRING_SOON"
    STATUS_EXPIRED = "STATUS_EXPIRED"
    STATUS_REOPENED = "STATUS_REOPENED"
    ALIAS_MERGED = "ALIAS_MERGED"


class EntityObservation(BaseModel):
    """
    EN: A timestamped observation of an entity harvested from an external source.
    DE: Eine mit Zeitstempel versehene Beobachtung einer Entität aus einer externen Quelle.
    """
    canonical_id: str = Field(..., description="Resolved canonical entity identifier")
    source_id: str = Field(..., description="Originating portal or skill identifier")
    raw_uri: str = Field(..., description="Observed source URI")
    title: str = Field(..., description="Observed entity title")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain key-value metadata")
    deadline_iso: Optional[str] = Field(default=None, description="ISO-8601 deadline date/datetime if present")
    valid_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Real-world validity timestamp of the observation"
    )
    transaction_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="System ingestion timestamp"
    )


class EntityNode(BaseModel):
    """
    EN: Longitudinal node in the TemporalEventGraph consolidating cross-source aliases and state.
    DE: Longitudinaler Knoten im TemporalEventGraph zur Konsolidierung quellenübergreifender Aliase.
    """
    canonical_id: str
    primary_title: str
    aliases: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    state: EntityLifecycleState = EntityLifecycleState.NEW
    attributes: Dict[str, Any] = Field(default_factory=dict)
    deadline_iso: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    observation_count: int = 1


class StateTransitionEdge(BaseModel):
    """
    EN: Directed bitemporal edge recording a state or attribute delta for an entity.
    DE: Gerichtete bitemporale Kante zur Aufzeichnung einer Zustands- oder Attributänderung.
    """
    edge_id: str
    canonical_id: str
    from_state: Optional[EntityLifecycleState] = None
    to_state: EntityLifecycleState
    transition: TransitionType
    delta: Dict[str, Tuple[Any, Any]] = Field(default_factory=dict)
    source_id: str
    valid_time: datetime
    transaction_time: datetime


class TemporalEventGraph:
    """
    EN: SQLite-backed bitemporal event graph tracking longitudinal entity evolution,
        deadline shifts, reopenings, and cross-source consolidation.
    DE: SQLite-gestützter bitemporaler Ereignisgraph für longitudinale Entitätsentwicklung,
        Fristverlängerungen, Wiedereröffnungen und quellenübergreifende Konsolidierung.
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_nodes (
                    canonical_id TEXT PRIMARY KEY,
                    primary_title TEXT NOT NULL,
                    aliases_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attributes_json TEXT NOT NULL,
                    deadline_iso TEXT,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    observation_count INTEGER NOT NULL DEFAULT 1
                )
            """)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS temporal_edges (
                    edge_id TEXT PRIMARY KEY,
                    canonical_id TEXT NOT NULL,
                    from_state TEXT,
                    to_state TEXT NOT NULL,
                    transition TEXT NOT NULL,
                    delta_json TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    valid_time TEXT NOT NULL,
                    transaction_time TEXT NOT NULL,
                    FOREIGN KEY (canonical_id) REFERENCES temporal_nodes(canonical_id)
                )
            """)
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_temporal_edges_canonical ON temporal_edges(canonical_id)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_temporal_nodes_state ON temporal_nodes(state)"
            )

    @staticmethod
    def _parse_deadline(deadline_iso: Optional[str]) -> Optional[datetime]:
        if not deadline_iso:
            return None
        try:
            cleaned = deadline_iso.strip().replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    def get_node(self, canonical_id: str) -> Optional[EntityNode]:
        cur = self._conn.execute(
            "SELECT * FROM temporal_nodes WHERE canonical_id = ?",
            (canonical_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return self._row_to_node(row)

    def list_nodes(self, state: Optional[EntityLifecycleState] = None) -> List[EntityNode]:
        if state is not None:
            cur = self._conn.execute(
                "SELECT * FROM temporal_nodes WHERE state = ? ORDER BY last_seen DESC",
                (state.value,),
            )
        else:
            cur = self._conn.execute("SELECT * FROM temporal_nodes ORDER BY last_seen DESC")
        return [self._row_to_node(r) for r in cur.fetchall()]

    def get_history(self, canonical_id: str) -> List[StateTransitionEdge]:
        cur = self._conn.execute(
            "SELECT * FROM temporal_edges WHERE canonical_id = ? ORDER BY valid_time ASC, transaction_time ASC",
            (canonical_id,),
        )
        return [self._row_to_edge(r) for r in cur.fetchall()]

    def ingest_observation(
        self,
        obs: EntityObservation,
        expiring_window_days: int = 14,
    ) -> StateTransitionEdge:
        """
        EN: Ingests a resolved entity observation, computes semantic state transitions,
            and records an immutable bitemporal transition edge.
        DE: Verarbeitet eine aufgelöste Entitätsbeobachtung, berechnet semantische
            Zustandsübergänge und speichert eine unveränderliche bitemporale Kante.
        """
        existing = self.get_node(obs.canonical_id)

        if existing is None:
            initial_state = EntityLifecycleState.NEW
            dl_dt = self._parse_deadline(obs.deadline_iso)
            if dl_dt is not None:
                if dl_dt < obs.valid_time:
                    initial_state = EntityLifecycleState.EXPIRED
                elif dl_dt <= obs.valid_time + timedelta(days=expiring_window_days):
                    initial_state = EntityLifecycleState.EXPIRING_SOON

            node = EntityNode(
                canonical_id=obs.canonical_id,
                primary_title=obs.title,
                aliases=[obs.title],
                sources=[obs.source_id],
                state=initial_state,
                attributes=dict(obs.attributes),
                deadline_iso=obs.deadline_iso,
                first_seen=obs.valid_time,
                last_seen=obs.valid_time,
                observation_count=1,
            )
            edge = self._make_edge(
                canonical_id=obs.canonical_id,
                from_state=None,
                to_state=initial_state,
                transition=TransitionType.CREATED,
                delta={"title": (None, obs.title)},
                source_id=obs.source_id,
                valid_time=obs.valid_time,
                transaction_time=obs.transaction_time,
            )
            with self._conn:
                self._upsert_node(node)
                self._insert_edge(edge)
            return edge

        # Compute field-level attribute deltas
        delta: Dict[str, Tuple[Any, Any]] = {}
        merged_attrs = dict(existing.attributes)
        for k, v in obs.attributes.items():
            old_v = merged_attrs.get(k)
            if old_v != v and v is not None:
                delta[k] = (old_v, v)
                merged_attrs[k] = v

        old_dl = self._parse_deadline(existing.deadline_iso)
        new_dl = self._parse_deadline(obs.deadline_iso)
        final_deadline_iso = obs.deadline_iso if obs.deadline_iso is not None else existing.deadline_iso

        if obs.deadline_iso and obs.deadline_iso != existing.deadline_iso:
            delta["deadline_iso"] = (existing.deadline_iso, obs.deadline_iso)

        is_new_alias = obs.title not in existing.aliases
        is_new_source = obs.source_id not in existing.sources
        if is_new_alias:
            delta["alias"] = (existing.primary_title, obs.title)
        if is_new_source:
            delta["source"] = (",".join(existing.sources), obs.source_id)

        from_state = existing.state
        to_state = existing.state
        transition = TransitionType.CONFIRMED_UNCHANGED

        if from_state in (EntityLifecycleState.EXPIRED, EntityLifecycleState.ARCHIVED) and (
            new_dl is None or new_dl > obs.valid_time
        ):
            to_state = EntityLifecycleState.REOPENED
            transition = TransitionType.STATUS_REOPENED
        elif old_dl is not None and new_dl is not None and new_dl > old_dl:
            to_state = EntityLifecycleState.DEADLINE_EXTENDED
            transition = TransitionType.DEADLINE_EXTENDED
        elif old_dl is not None and new_dl is not None and new_dl < old_dl:
            to_state = EntityLifecycleState.UPDATED
            transition = TransitionType.DEADLINE_SHORTENED
        elif new_dl is not None and new_dl < obs.valid_time and from_state != EntityLifecycleState.EXPIRED:
            to_state = EntityLifecycleState.EXPIRED
            transition = TransitionType.STATUS_EXPIRED
        elif (
            new_dl is not None
            and obs.valid_time <= new_dl <= obs.valid_time + timedelta(days=expiring_window_days)
            and from_state not in (EntityLifecycleState.EXPIRING_SOON, EntityLifecycleState.EXPIRED)
        ):
            to_state = EntityLifecycleState.EXPIRING_SOON
            transition = TransitionType.STATUS_EXPIRING_SOON
        elif is_new_alias or is_new_source:
            to_state = EntityLifecycleState.ACTIVE if from_state == EntityLifecycleState.NEW else from_state
            transition = TransitionType.ALIAS_MERGED
        elif delta:
            to_state = EntityLifecycleState.UPDATED
            transition = TransitionType.ATTRIBUTE_UPDATED
        else:
            to_state = EntityLifecycleState.ACTIVE if from_state == EntityLifecycleState.NEW else from_state
            transition = TransitionType.CONFIRMED_UNCHANGED

        aliases = list(dict.fromkeys([*existing.aliases, obs.title]))
        sources = list(dict.fromkeys([*existing.sources, obs.source_id]))

        updated_node = EntityNode(
            canonical_id=existing.canonical_id,
            primary_title=existing.primary_title,
            aliases=aliases,
            sources=sources,
            state=to_state,
            attributes=merged_attrs,
            deadline_iso=final_deadline_iso,
            first_seen=existing.first_seen,
            last_seen=max(existing.last_seen, obs.valid_time),
            observation_count=existing.observation_count + 1,
        )
        edge = self._make_edge(
            canonical_id=existing.canonical_id,
            from_state=from_state,
            to_state=to_state,
            transition=transition,
            delta=delta,
            source_id=obs.source_id,
            valid_time=obs.valid_time,
            transaction_time=obs.transaction_time,
        )
        with self._conn:
            self._upsert_node(updated_node)
            self._insert_edge(edge)
        return edge

    def sweep_temporal_horizons(
        self,
        reference_time: Optional[datetime] = None,
        expiring_window_days: int = 14,
    ) -> List[StateTransitionEdge]:
        """
        EN: Autonomously evaluates all non-expired nodes against reference_time to emit
            time-driven transitions (EXPIRING_SOON, EXPIRED) even without new crawls.
        DE: Bewertet alle aktiven Knoten gegen reference_time und erzeugt zeitgesteuerte
            Zustandsübergänge (EXPIRING_SOON, EXPIRED) auch ohne neue Web-Abrufe.
        """
        now = reference_time or datetime.now(timezone.utc)
        cur = self._conn.execute(
            "SELECT * FROM temporal_nodes WHERE state NOT IN (?, ?)",
            (EntityLifecycleState.EXPIRED.value, EntityLifecycleState.ARCHIVED.value),
        )
        emitted: List[StateTransitionEdge] = []
        for row in cur.fetchall():
            dl_dt = self._parse_deadline(row["deadline_iso"])
            if dl_dt is None:
                continue

            from_state = EntityLifecycleState(row["state"])
            to_state: Optional[EntityLifecycleState] = None
            transition: Optional[TransitionType] = None

            if dl_dt < now:
                to_state = EntityLifecycleState.EXPIRED
                transition = TransitionType.STATUS_EXPIRED
            elif (
                dl_dt <= now + timedelta(days=expiring_window_days)
                and from_state != EntityLifecycleState.EXPIRING_SOON
            ):
                to_state = EntityLifecycleState.EXPIRING_SOON
                transition = TransitionType.STATUS_EXPIRING_SOON

            if to_state is not None and transition is not None:
                edge = self._make_edge(
                    canonical_id=row["canonical_id"],
                    from_state=from_state,
                    to_state=to_state,
                    transition=transition,
                    delta={"state": (from_state.value, to_state.value)},
                    source_id="temporal_horizon_sweep",
                    valid_time=now,
                    transaction_time=now,
                )
                with self._conn:
                    self._conn.execute(
                        "UPDATE temporal_nodes SET state = ? WHERE canonical_id = ?",
                        (to_state.value, row["canonical_id"]),
                    )
                    self._insert_edge(edge)
                emitted.append(edge)

        return emitted

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _make_edge(
        canonical_id: str,
        from_state: Optional[EntityLifecycleState],
        to_state: EntityLifecycleState,
        transition: TransitionType,
        delta: Dict[str, Tuple[Any, Any]],
        source_id: str,
        valid_time: datetime,
        transaction_time: datetime,
    ) -> StateTransitionEdge:
        raw = (
            f"{canonical_id}|{transition.value}|{valid_time.isoformat()}|"
            f"{transaction_time.isoformat()}|{json.dumps(delta, sort_keys=True, default=str)}"
        )
        edge_id = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        return StateTransitionEdge(
            edge_id=edge_id,
            canonical_id=canonical_id,
            from_state=from_state,
            to_state=to_state,
            transition=transition,
            delta=delta,
            source_id=source_id,
            valid_time=valid_time,
            transaction_time=transaction_time,
        )

    def _upsert_node(self, node: EntityNode) -> None:
        self._conn.execute("""
            INSERT INTO temporal_nodes (
                canonical_id, primary_title, aliases_json, sources_json,
                state, attributes_json, deadline_iso, first_seen, last_seen, observation_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(canonical_id) DO UPDATE SET
                aliases_json = excluded.aliases_json,
                sources_json = excluded.sources_json,
                state = excluded.state,
                attributes_json = excluded.attributes_json,
                deadline_iso = excluded.deadline_iso,
                last_seen = excluded.last_seen,
                observation_count = excluded.observation_count
        """, (
            node.canonical_id,
            node.primary_title,
            json.dumps(node.aliases, ensure_ascii=False),
            json.dumps(node.sources, ensure_ascii=False),
            node.state.value,
            json.dumps(node.attributes, ensure_ascii=False, default=str),
            node.deadline_iso,
            node.first_seen.isoformat(),
            node.last_seen.isoformat(),
            node.observation_count,
        ))

    def _insert_edge(self, edge: StateTransitionEdge) -> None:
        self._conn.execute("""
            INSERT OR IGNORE INTO temporal_edges (
                edge_id, canonical_id, from_state, to_state, transition,
                delta_json, source_id, valid_time, transaction_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            edge.edge_id,
            edge.canonical_id,
            edge.from_state.value if edge.from_state else None,
            edge.to_state.value,
            edge.transition.value,
            json.dumps(edge.delta, ensure_ascii=False, default=str),
            edge.source_id,
            edge.valid_time.isoformat(),
            edge.transaction_time.isoformat(),
        ))

    @staticmethod
    def _row_to_node(row: sqlite3.Row) -> EntityNode:
        return EntityNode(
            canonical_id=row["canonical_id"],
            primary_title=row["primary_title"],
            aliases=json.loads(row["aliases_json"]),
            sources=json.loads(row["sources_json"]),
            state=EntityLifecycleState(row["state"]),
            attributes=json.loads(row["attributes_json"]),
            deadline_iso=row["deadline_iso"],
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            observation_count=row["observation_count"],
        )

    @staticmethod
    def _row_to_edge(row: sqlite3.Row) -> StateTransitionEdge:
        raw_delta = json.loads(row["delta_json"])
        typed_delta: Dict[str, Tuple[Any, Any]] = {
            k: (v[0], v[1]) for k, v in raw_delta.items() if isinstance(v, list) and len(v) == 2
        }
        return StateTransitionEdge(
            edge_id=row["edge_id"],
            canonical_id=row["canonical_id"],
            from_state=EntityLifecycleState(row["from_state"]) if row["from_state"] else None,
            to_state=EntityLifecycleState(row["to_state"]),
            transition=TransitionType(row["transition"]),
            delta=typed_delta,
            source_id=row["source_id"],
            valid_time=datetime.fromisoformat(row["valid_time"]),
            transaction_time=datetime.fromisoformat(row["transaction_time"]),
        )
