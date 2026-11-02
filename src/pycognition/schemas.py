# Version: 0.1.0 | Release Date: 2026-11-02
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from pydantic import BaseModel, Field


class CognitiveTrack(str, Enum):
    """Когнитивная траектория обработки задачи."""
    SYSTEM_1 = "system_1"
    SYSTEM_2 = "system_2"


class ExecutionStatus(str, Enum):
    """Статус завершения исполнения."""
    SUCCESS = "success"
    FAILURE = "failure"
    FALLBACK_REQUIRED = "fallback_required"


class Task(BaseModel):
    """Модель входящей задачи для когнитивной системы."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = Field(..., description="Текстовая формулировка задачи")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Структурированные входные данные",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Контекстные метаданные задачи",
    )


class SkillSignature(BaseModel):
    """Формальное описание интерфейса процедурного навыка."""
    name: str = Field(..., description="Уникальный идентификатор навыка")
    description: str = Field(..., description="Семантическое назначение скрипта")
    parameters_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON-схема входных аргументов",
    )
    return_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON-схема возвращаемого результата",
    )
    version: str = "0.1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RoutingDecision(BaseModel):
    """Решение арбитра о маршрутизации задачи."""
    selected_track: CognitiveTrack
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    matched_skill: Optional[SkillSignature] = None
    reasoning: str = Field(..., description="Обоснование решения арбитра")


class ExecutionResult(BaseModel):
    """Итоговый результат обработки задачи выбранным контуром."""
    task_id: str
    track_used: CognitiveTrack
    status: ExecutionStatus
    output: Any
    latency_ms: float
    token_usage: Optional[Dict[str, int]] = None
    error_message: Optional[str] = None
