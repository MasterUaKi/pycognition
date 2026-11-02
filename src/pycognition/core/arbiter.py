# Version: 0.1.0 | Release Date: 2026-11-02
from abc import ABC, abstractmethod
from pycognition.schemas import RoutingDecision, Task


class BaseArbiter(ABC):
    """
    Интерфейс Арбитра: механизм динамического переключения между Системой 1 и Системой 2.
    """

    @abstractmethod
    async def route(self, task: Task) -> RoutingDecision:
        """Оценивает уверенность и определяет целевой контур исполнения."""
        pass

    @abstractmethod
    def set_confidence_threshold(self, threshold: float) -> None:
        """Устанавливает порог отсечения для направления задачи в быстрый процедурный контур."""
        pass
