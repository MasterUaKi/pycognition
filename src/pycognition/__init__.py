# Version: 0.1.0 | Release Date: 2026-11-02
"""
pycognition: Фреймворк двухуровневой когнитивной архитектуры (Система 1 / Система 2).
"""

from pycognition.engine.runtime import CognitiveRuntime
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    ExecutionStatus,
    RoutingDecision,
    SkillSignature,
    Task,
)

__version__ = "0.1.0"
__author__ = "Oleh Riabtsev"
__license__ = "LGPL-3.0-or-later"

__all__ = [
    "CognitiveRuntime",
    "CognitiveTrack",
    "ExecutionResult",
    "ExecutionStatus",
    "RoutingDecision",
    "SkillSignature",
    "Task",
]
