# Version: 0.1.0 | Release Date: 2026-11-02
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from pycognition.schemas import ExecutionResult, SkillSignature, Task


class BaseMemory(ABC):
    """
    Интерфейс гибридной памяти: хранение процедурного кода, векторных индексов и истории решений.
    """

    @abstractmethod
    async def save_skill_code(self, signature: SkillSignature, code: str, tests: str) -> None:
        """Сохраняет исходный код и набор тестов синтезированного навыка."""
        pass

    @abstractmethod
    async def find_matching_skill(self, task: Task) -> Optional[Tuple[SkillSignature, float]]:
        """Ищет подходящий навык и возвращает оценку семантического сходства (0.0 - 1.0)."""
        pass

    @abstractmethod
    async def log_execution(self, task: Task, result: ExecutionResult) -> None:
        """Фиксирует трассу выполнения задачи."""
        pass
