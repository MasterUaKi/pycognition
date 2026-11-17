# File: src/pycognition/temporal/resolver.py
# Version: 1.3.2 | Release Date: 2026-11-17
# EN: Dual-tier neuro-symbolic cross-source entity resolver with crystallized alias memory.
# DE: Zweistufiger neuro-symbolischer quellenübergreifender Entitätsauflöser mit Alias-Gedächtnis.

from __future__ import annotations

import hashlib
import inspect
import re
import sqlite3
import unicodedata
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set
from pydantic import BaseModel

from pycognition.temporal.graph import EntityNode


class ResolutionTrack(str, Enum):
    """
    EN: Execution tier used to resolve an entity observation.
    DE: Ausführungsebene zur Auflösung einer Entitätsbeobachtung.
    """
    CACHE_HIT = "CACHE_HIT"                  # Crystallized alias memory (0 LLM tokens)
    SYSTEM1_LEXICAL = "SYSTEM1_LEXICAL"      # High-confidence deterministic match (0 LLM tokens)
    SYSTEM1_DISTINCT = "SYSTEM1_DISTINCT"    # Low similarity deterministic new entity (0 LLM tokens)
    SYSTEM2_SEMANTIC = "SYSTEM2_SEMANTIC"    # Gray-zone LLM semantic arbitration (amortized 1-time)


class ResolutionDecision(BaseModel):
    """
    EN: Auditable output of cross-source entity resolution.
    DE: Nachvollziehbares Ergebnis der quellenübergreifenden Entitätsauflösung.
    """
    canonical_id: str
    is_new_entity: bool
    matched_existing_id: Optional[str] = None
    similarity_score: float
    track_used: ResolutionTrack
    llm_invoked: bool = False
    rationale: str = ""


class AliasMemoryStore:
    """
    EN: Persistent SQLite memory caching crystallized positive alias mappings and
        confirmed negative (non-equivalent) pairs to guarantee zero-token recurrence.
    DE: Persistentes SQLite-Gedächtnis für kristallisierte positive Alias-Zuordnungen und
        bestätigte negative Paare zur Vermeidung wiederholter LLM-Aufrufe.
    """

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS alias_mappings (
                    normalized_sig TEXT PRIMARY KEY,
                    canonical_id TEXT NOT NULL,
                    raw_title TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS negative_pairs (
                    pair_key TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
            """)

    def lookup_alias(self, normalized_sig: str) -> Optional[str]:
        cur = self._conn.execute(
            "SELECT canonical_id FROM alias_mappings WHERE normalized_sig = ?",
            (normalized_sig,),
        )
        row = cur.fetchone()
        return str(row["canonical_id"]) if row else None

    def crystallize_alias(
        self,
        normalized_sig: str,
        canonical_id: str,
        raw_title: str,
        source_id: str,
    ) -> None:
        with self._conn:
            self._conn.execute("""
                INSERT OR REPLACE INTO alias_mappings (
                    normalized_sig, canonical_id, raw_title, source_id, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                normalized_sig,
                canonical_id,
                raw_title,
                source_id,
                datetime.now(timezone.utc).isoformat(),
            ))

    @staticmethod
    def _pair_key(sig_a: str, sig_b: str) -> str:
        a, b = sorted([sig_a, sig_b])
        return hashlib.sha256(f"{a}||{b}".encode("utf-8")).hexdigest()

    def is_known_distinct(self, sig_a: str, sig_b: str) -> bool:
        pk = self._pair_key(sig_a, sig_b)
        cur = self._conn.execute("SELECT 1 FROM negative_pairs WHERE pair_key = ?", (pk,))
        return cur.fetchone() is not None

    def record_distinct_pair(self, sig_a: str, sig_b: str) -> None:
        pk = self._pair_key(sig_a, sig_b)
        with self._conn:
            self._conn.execute(
                "INSERT OR IGNORE INTO negative_pairs (pair_key, created_at) VALUES (?, ?)",
                (pk, datetime.now(timezone.utc).isoformat()),
            )

    def close(self) -> None:
        self._conn.close()


# Type alias for System 2 semantic equivalence callback
SemanticArbiterFn = Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[bool] | bool]


class NeuroSymbolicEntityResolver:
    """
    EN: Resolves incoming entity observations against existing TemporalEventGraph nodes.
        Uses System 1 lexical/structural similarity + institutional blocking anchors for
        clear matches/non-matches, and invokes System 2 semantic arbitration inside the
        gray zone [low, high), crystallizing every System 2 decision into AliasMemoryStore.
    DE: Löst eingehende Entitätsbeobachtungen gegen bestehende Knoten auf. Nutzt System-1-
        Ähnlichkeit + institutionelle Anker für eindeutige Fälle und System-2-Arbitrierung
        in der Grauzone [low, high), wobei jede Entscheidung im AliasMemoryStore gespeichert wird.
    """

    STOPWORDS: Set[str] = {
        "the", "and", "for", "with", "from", "into", "der", "die", "das",
        "und", "für", "fur", "von", "mit", "zur", "zum", "des", "den", "dem",
    }

    def __init__(
        self,
        alias_store: Optional[AliasMemoryStore] = None,
        high_confidence_threshold: float = 0.90,
        low_confidence_threshold: float = 0.42,
        semantic_arbiter: Optional[SemanticArbiterFn] = None,
    ) -> None:
        self.alias_store = alias_store or AliasMemoryStore(":memory:")
        self.high_threshold = high_confidence_threshold
        self.low_threshold = low_confidence_threshold
        self.semantic_arbiter = semantic_arbiter

    @classmethod
    def normalize_title(cls, title: str) -> str:
        """
        EN: Produces a diacritic-folded, token-normalized canonical signature string.
        DE: Erzeugt eine diakritikbereinigte, token-normalisierte kanonische Signatur.
        """
        nfkd = unicodedata.normalize("NFKD", title.lower().strip())
        ascii_folded = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
        tokens = re.findall(r"[a-z0-9]+", ascii_folded)
        filtered = [t for t in tokens if len(t) > 1 and t not in cls.STOPWORDS]
        return " ".join(filtered) if filtered else " ".join(tokens)

    @staticmethod
    def _extract_acronyms(title: str) -> Set[str]:
        """
        EN: Extracts uppercase institutional/program acronyms (length >= 3) as blocking keys.
        DE: Extrahiert großgeschriebene institutionelle Akronyme (Länge >= 3) als Blocking-Keys.
        """
        return {tok for tok in re.findall(r"\b[A-ZÄÖÜ]{3,}\b", title)}

    @classmethod
    def compute_similarity(
        cls,
        title_a: str,
        title_b: str,
        deadline_a: Optional[str] = None,
        deadline_b: Optional[str] = None,
        funder_a: Optional[str] = None,
        funder_b: Optional[str] = None,
    ) -> float:
        """
        EN: Hybrid System 1 similarity combining token Jaccard, character bigram Dice,
            non-redundant institutional blocking anchors, and deadline alignment boosts.
        DE: Hybride System-1-Ähnlichkeit aus Token-Jaccard, Zeichen-Bigramm-Dice,
            institutionellen Akronym-Ankern und Frist-Abgleich.
        """
        sig_a = cls.normalize_title(title_a)
        sig_b = cls.normalize_title(title_b)
        if not sig_a or not sig_b:
            return 0.0
        if sig_a == sig_b:
            return 1.0

        tokens_a = set(sig_a.split())
        tokens_b = set(sig_b.split())
        jaccard = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))

        bigrams_a = {sig_a[i:i + 2] for i in range(max(1, len(sig_a) - 1))}
        bigrams_b = {sig_b[i:i + 2] for i in range(max(1, len(sig_b) - 1))}
        dice = (2.0 * len(bigrams_a & bigrams_b)) / max(1, (len(bigrams_a) + len(bigrams_b)))

        base_score = 0.55 * jaccard + 0.45 * dice

        boost = 0.0
        acr_a = cls._extract_acronyms(title_a)
        acr_b = cls._extract_acronyms(title_b)
        same_funder = bool(
            funder_a and funder_b and cls.normalize_title(funder_a) == cls.normalize_title(funder_b)
        )
        same_acronym = bool(acr_a and acr_b and (acr_a & acr_b))
        if same_funder or same_acronym:
            boost += 0.14

        if deadline_a and deadline_b and deadline_a.strip()[:10] == deadline_b.strip()[:10]:
            boost += 0.08

        return min(1.0, base_score + boost)

    @staticmethod
    def generate_canonical_id(normalized_sig: str, seed_uri: str = "") -> str:
        raw = f"{normalized_sig}|{seed_uri.strip().lower()}"
        return "ent_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    async def resolve_async(
        self,
        title: str,
        source_id: str,
        raw_uri: str,
        existing_nodes: List[EntityNode],
        deadline_iso: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> ResolutionDecision:
        """
        EN: Asynchronously resolves an observation against existing graph nodes, invoking
            an async or sync System 2 semantic arbiter only for gray-zone candidates.
        DE: Löst eine Beobachtung asynchron gegen bestehende Knoten auf und ruft bei
            Grauzonen-Kandidaten den System-2-Arbitrierer auf.
        """
        attrs = attributes or {}
        funder = str(attrs.get("funder") or source_id)
        norm_sig = self.normalize_title(title)

        # Tier 0: Crystallized Alias Memory Lookup (0 LLM calls)
        cached_id = self.alias_store.lookup_alias(norm_sig)
        if cached_id is not None:
            return ResolutionDecision(
                canonical_id=cached_id,
                is_new_entity=False,
                matched_existing_id=cached_id,
                similarity_score=1.0,
                track_used=ResolutionTrack.CACHE_HIT,
                llm_invoked=False,
                rationale="Resolved via crystallized alias memory cache.",
            )

        # Tier 1: System 1 Candidate Scoring
        best_node: Optional[EntityNode] = None
        best_score = 0.0

        for node in existing_nodes:
            node_funder = str(node.attributes.get("funder") or (node.sources[0] if node.sources else ""))
            for alias in node.aliases:
                score = self.compute_similarity(
                    title_a=title,
                    title_b=alias,
                    deadline_a=deadline_iso,
                    deadline_b=node.deadline_iso,
                    funder_a=funder,
                    funder_b=node_funder,
                )
                if score > best_score:
                    best_score = score
                    best_node = node

        if best_node is not None and best_score >= self.high_threshold:
            self.alias_store.crystallize_alias(norm_sig, best_node.canonical_id, title, source_id)
            return ResolutionDecision(
                canonical_id=best_node.canonical_id,
                is_new_entity=False,
                matched_existing_id=best_node.canonical_id,
                similarity_score=best_score,
                track_used=ResolutionTrack.SYSTEM1_LEXICAL,
                llm_invoked=False,
                rationale=f"High lexical/structural similarity ({best_score:.3f} >= {self.high_threshold}).",
            )

        # Tier 2: Gray-Zone System 2 Semantic Arbitration
        if (
            best_node is not None
            and self.low_threshold <= best_score < self.high_threshold
            and self.semantic_arbiter is not None
        ):
            best_sig = self.normalize_title(best_node.primary_title)
            if not self.alias_store.is_known_distinct(norm_sig, best_sig):
                candidate_a = {
                    "title": title,
                    "source_id": source_id,
                    "deadline_iso": deadline_iso,
                    "attributes": attrs,
                }
                candidate_b = {
                    "title": best_node.primary_title,
                    "aliases": best_node.aliases,
                    "sources": best_node.sources,
                    "deadline_iso": best_node.deadline_iso,
                    "attributes": best_node.attributes,
                }
                verdict = self.semantic_arbiter(candidate_a, candidate_b)
                if inspect.isawaitable(verdict):
                    verdict = await verdict

                if bool(verdict):
                    self.alias_store.crystallize_alias(
                        norm_sig, best_node.canonical_id, title, source_id
                    )
                    return ResolutionDecision(
                        canonical_id=best_node.canonical_id,
                        is_new_entity=False,
                        matched_existing_id=best_node.canonical_id,
                        similarity_score=best_score,
                        track_used=ResolutionTrack.SYSTEM2_SEMANTIC,
                        llm_invoked=True,
                        rationale=f"System 2 confirmed cross-source equivalence (score={best_score:.3f}) and crystallized alias.",
                    )
                else:
                    self.alias_store.record_distinct_pair(norm_sig, best_sig)

        # Create New Canonical Entity
        new_id = self.generate_canonical_id(norm_sig, raw_uri)
        self.alias_store.crystallize_alias(norm_sig, new_id, title, source_id)
        return ResolutionDecision(
            canonical_id=new_id,
            is_new_entity=True,
            matched_existing_id=None,
            similarity_score=best_score,
            track_used=ResolutionTrack.SYSTEM1_DISTINCT,
            llm_invoked=False,
            rationale=f"Distinct entity registered (max similarity={best_score:.3f}).",
        )
