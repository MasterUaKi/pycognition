# File: src/pycognition/skills/telemetry.py
# Version: 1.2.0 | Release Date: 2026-11-12
# EN: Quantitative execution telemetry and structural degradation detector for System 1 skills.
# DE: Quantitative Ausführungstelemetrie und Erkennung struktureller Degradation für System-1-Skills.

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class AnomalyThresholds(BaseModel):
    """
    EN: Configurable thresholds governing when System 1 degradation triggers System 2 refactoring.
    DE: Konfigurierbare Schwellenwerte, ab denen eine System-1-Degradation ein System-2-Refactoring auslöst.
    """
    max_corruption_ratio: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Maximum tolerable ratio of invalid/empty records before declaring skill degradation"
    )
    min_sample_size_for_ratio: int = Field(
        default=3,
        ge=1,
        description="Minimum raw candidate count required to evaluate corruption_ratio"
    )
    trigger_on_zero_yield_first_pass: bool = Field(
        default=True,
        description="Trigger System 2 synthesis/refactoring if an initial pass yields zero valid items"
    )


class SkillExecutionTelemetry(BaseModel):
    """
    EN: Structured health report produced after every procedural System 1 execution.
    DE: Strukturierter Zustandsbericht nach jeder prozeduralen System-1-Ausführung.
    """
    skill_name: str
    target_uri: str
    total_raw_candidates: int = 0
    valid_records: List[Dict[str, Any]] = Field(default_factory=list)
    corrupt_samples: List[str] = Field(default_factory=list)
    execution_error: Optional[str] = None
    thresholds: AnomalyThresholds = Field(default_factory=AnomalyThresholds)

    @property
    def valid_count(self) -> int:
        return len(self.valid_records)

    @property
    def corrupt_count(self) -> int:
        return max(0, self.total_raw_candidates - self.valid_count)

    @property
    def corruption_ratio(self) -> float:
        if self.total_raw_candidates == 0:
            return 0.0
        return self.corrupt_count / self.total_raw_candidates

    @property
    def is_degraded(self) -> bool:
        """
        EN: Returns True if runtime exceptions or structural noise exceed configured tolerances.
        DE: Gibt True zurück, wenn Laufzeitfehler oder strukturelles Rauschen die Toleranz überschreiten.
        """
        if self.execution_error:
            return True
        if (
            self.total_raw_candidates >= self.thresholds.min_sample_size_for_ratio
            and self.corruption_ratio > self.thresholds.max_corruption_ratio
        ):
            return True
        return False

    def to_diagnostic_prompt(self) -> str:
        """
        EN: Formats an actionable diagnostic report for System 2 architectural reflection.
        DE: Erstellt einen strukturierten Diagnosebericht für die architektonische System-2-Reflexion.
        """
        if self.execution_error:
            return (
                f"RUNTIME EXCEPTION in System 1 skill '{self.skill_name}' on {self.target_uri}:\n"
                f"{self.execution_error}"
            )

        preview = ", ".join(repr(s) for s in self.corrupt_samples[:6])
        return (
            f"STRUCTURAL DEGRADATION REPORT:\n"
            f"- Skill: {self.skill_name}\n"
            f"- Target URI: {self.target_uri}\n"
            f"- Raw candidates matched: {self.total_raw_candidates}\n"
            f"- Valid records: {self.valid_count}\n"
            f"- Corrupt/empty records: {self.corrupt_count} ({self.corruption_ratio:.1%})\n"
            f"- Sample invalid captures: [{preview}]\n"
            f"DIAGNOSIS: Selectors or extraction filters inside the procedural skill match structural "
            f"noise or miss target entities. Refactor the extraction logic to eliminate empty captures."
        )


class TelemetryEvaluator:
    """
    EN: Domain-agnostic evaluator separating valid structured records from phantom/corrupt captures.
    DE: Domänenunabhängiger Evaluator zur Trennung valider Datensätze von Phantom-/Fehler-Einträgen.
    """

    DEFAULT_REFUSAL_MARKERS: Tuple[str, ...] = (
        "cannot extract",
        "can't extract",
        "snippet is empty",
        "no title",
        "не удалось извлечь",
        "не могу извлечь",
        "фрагмент пуст",
        "nicht extrahiert werden",
    )

    def __init__(
        self,
        required_key: str = "title",
        min_length: int = 5,
        max_length: int = 300,
        thresholds: Optional[AnomalyThresholds] = None,
        custom_validator: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> None:
        self.required_key = required_key
        self.min_length = min_length
        self.max_length = max_length
        self.thresholds = thresholds or AnomalyThresholds()
        self.custom_validator = custom_validator

    def evaluate(
        self,
        skill_name: str,
        target_uri: str,
        raw_output: Any,
        execution_error: Optional[str] = None,
    ) -> SkillExecutionTelemetry:
        telemetry = SkillExecutionTelemetry(
            skill_name=skill_name,
            target_uri=target_uri,
            execution_error=execution_error,
            thresholds=self.thresholds,
        )

        if execution_error is not None:
            return telemetry

        if not isinstance(raw_output, list):
            telemetry.execution_error = f"Expected list output from skill, received {type(raw_output).__name__}."
            return telemetry

        telemetry.total_raw_candidates = len(raw_output)

        for item in raw_output:
            if not isinstance(item, dict):
                telemetry.corrupt_samples.append(repr(item)[:80])
                continue

            if self._is_record_valid(item):
                telemetry.valid_records.append(item)
            else:
                bad_val = str(item.get(self.required_key) or "<EMPTY>").strip()
                telemetry.corrupt_samples.append(bad_val[:80])

        return telemetry

    def _is_record_valid(self, record: Dict[str, Any]) -> bool:
        raw_val = str(record.get(self.required_key) or "").strip()
        cleaned = re.sub(r"\s+", " ", raw_val).strip()

        if len(cleaned) < self.min_length or len(cleaned) > self.max_length:
            return False

        if len(re.findall(r"[A-Za-zА-Яа-яЁёÄÖÜäöüß0-9]", cleaned)) < 3:
            return False

        lowered = cleaned.lower()
        if any(marker in lowered for marker in self.DEFAULT_REFUSAL_MARKERS):
            return False

        if self.custom_validator is not None:
            return bool(self.custom_validator(record))

        return True
