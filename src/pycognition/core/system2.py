# Version: 0.1.0 | Release Date: 2026-11-02
from abc import ABC, abstractmethod
from typing import Optional
from pycognition.schemas import ExecutionResult, SkillSignature, Task


class BaseSystem2(ABC):
    """
    Интерфейс Системы 2: делиберативный контур.
    Оркестрирует запросы к LLM (OpenAI, DeepSeek), выполняет планирование и синтезирует скрипты.
    """

    @abstractmethod
    async def deliberate(self, task: Task) -> ExecutionResult:
        """Решает сложную задачу через глубокий логический вывод модели."""
        pass

    @abstractmethod
    async def synthesize_skill(self, task: Task, solution_context: str) -> Optional[SkillSignature]:
        """Кристаллизует решение задачи в детерминированный Python-скрипт с тестами."""
        pass
