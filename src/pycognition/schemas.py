# Version: 0.3.2 | Release Date: 2026-11-09
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class SkillCapability(str, Enum):
    """Профили прав и возможностей исполнения синтезируемых процедурных навыков."""
    GENERAL = "GENERAL"
    PURE_COMPUTATION = "PURE_COMPUTATION"
    DATA_TRANSFORMATION = "DATA_TRANSFORMATION"
    DATA_EXTRACTOR = "DATA_EXTRACTOR"


class ExecutionStatus(str, Enum):
    """Статусы жизненного цикла задач и вызовов навыков."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"
    RETRY = "RETRY"


class CognitiveTrack(str, Enum):
    """Когнитивные треки исполнения задач в рантайме."""
    SYSTEM_1 = "SYSTEM_1"
    SYSTEM_2 = "SYSTEM_2"
    FAST = "FAST"
    DELIBERATIVE = "DELIBERATIVE"
    PROCEDURAL = "PROCEDURAL"
    HYBRID = "HYBRID"


class SystemRoute(str, Enum):
    """Направления маршрутизации когнитивных задач."""
    SYSTEM_1 = "SYSTEM_1"
    SYSTEM_2 = "SYSTEM_2"
    HYBRID = "HYBRID"
    FALLBACK = "FALLBACK"


class RoutingDecision(BaseModel):
    """Решение мета-арбитра о выборе исполнительного контура (Система 1 / Система 2)."""
    route: str = "SYSTEM_1"
    target_system: str = "SYSTEM_1"
    decision: str = "SYSTEM_1"
    confidence: float = 1.0
    skill_name: Optional[str] = None
    reason: Optional[str] = ""
    rationale: Optional[str] = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    SYSTEM_1: ClassVar[Any] = None
    SYSTEM_2: ClassVar[Any] = None
    FALLBACK: ClassVar[Any] = None

    def __init__(self, *args, **data):
        if args and isinstance(args[0], (str, Enum)):
            val = args[0].value if isinstance(args[0], Enum) else args[0]
            data.setdefault("route", val)
            data.setdefault("target_system", val)
            data.setdefault("decision", val)
        super().__init__(**data)

    @property
    def value(self) -> str:
        return self.route

    @property
    def name(self) -> str:
        return self.route

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.route == other or self.target_system == other or self.decision == other
        if isinstance(other, Enum):
            return self.route == other.value or self.target_system == other.value
        if isinstance(other, RoutingDecision):
            return self.route == other.route
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(self.route)


RoutingDecision.SYSTEM_1 = RoutingDecision(route="SYSTEM_1", target_system="SYSTEM_1", decision="SYSTEM_1", confidence=1.0)
RoutingDecision.SYSTEM_2 = RoutingDecision(route="SYSTEM_2", target_system="SYSTEM_2", decision="SYSTEM_2", confidence=1.0)
RoutingDecision.FALLBACK = RoutingDecision(route="FALLBACK", target_system="FALLBACK", decision="FALLBACK", confidence=0.0)


class SkillSignature(BaseModel):
    """Метаданные и сигнатура процедурного навыка Системы 1."""
    name: str
    description: Optional[str] = ""
    capability: SkillCapability = SkillCapability.GENERAL
    parameters: Dict[str, Any] = Field(default_factory=dict)
    return_type: Optional[str] = "Any"
    docstring: Optional[str] = ""
    created_at: Optional[str] = None
    version: Optional[str] = "1.0.0"


class Task(BaseModel):
    """Единица когнитивной работы в рантайме pycognition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = Field(default_factory=dict)


class DeliberationResult(BaseModel):
    """Результат рассуждения Системы 2 (LLMDeliberator)."""
    task_id: Optional[str] = None
    output: Any = None
    result: Any = None
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    tokens_used: int = 0
    confidence: float = 1.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Результат детерминированного выполнения Системой 1."""
    task_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    output: Any = None
    result: Any = None
    execution_time_sec: float = 0.0
    tokens_used: int = 0
    error: Optional[str] = None