# Version: 0.1.0 | Release Date: 2026-11-02
from abc import ABC, abstractmethod
from typing import Any, Callable
from pycognition.schemas import ExecutionResult, SkillSignature, Task


class BaseSystem1(ABC):
    """
    Интерфейс Системы 1: процедурный контур.
    Обеспечивает строгое, быстрое и детерминированное исполнение скриптов без привлечения LLM.
    """

    @abstractmethod
    def register_skill(self, signature: SkillSignature, handler: Callable[..., Any]) -> None:
        """Регистрирует исполняемый скрипт в активном процедурном реестре."""
        pass

    @abstractmethod
    def has_skill(self, skill_name: str) -> bool:
        """Проверяет наличие навыка в реестре."""
        pass

    @abstractmethod
    async def execute(self, skill_name: str, task: Task) -> ExecutionResult:
        """Выполняет детерминированный скрипт с изоляцией исключений и замером времени."""
        pass
