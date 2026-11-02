# Version: 0.1.0 | Release Date: 2026-11-02
import asyncio
import inspect
import time
from typing import Any, Callable, Dict, Tuple

from pycognition.core.system1 import BaseSystem1
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    ExecutionStatus,
    SkillSignature,
    Task,
)


class ProceduralRunner(BaseSystem1):
    """
    Исполнитель процедурного контура (Система 1).
    Обеспечивает строгое, детерминированное выполнение зарегистрированных Python-скриптов
    без привлечения нейросетевых моделей с субмиллисекундной задержкой.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Tuple[SkillSignature, Callable[..., Any]]] = {}

    def register_skill(self, signature: SkillSignature, handler: Callable[..., Any]) -> None:
        """
        Регистрирует исполняемую функцию в процедурной памяти Системы 1.
        """
        self._registry[signature.name] = (signature, handler)

    def has_skill(self, skill_name: str) -> bool:
        """
        Проверяет наличие навыка в активном реестре.
        """
        return skill_name in self._registry

    async def execute(self, skill_name: str, task: Task) -> ExecutionResult:
        """
        Выполняет процедурный скрипт. Поддерживает как синхронные, так и асинхронные функции,
        изолирует необработанные исключения и замеряет точное время работы в миллисекундах.
        """
        start_time = time.perf_counter()

        if not self.has_skill(skill_name):
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_1,
                status=ExecutionStatus.FAILURE,
                output=None,
                latency_ms=latency_ms,
                error_message=f"Навык '{skill_name}' не зарегистрирован в Системе 1.",
            )

        _, handler = self._registry[skill_name]

        try:
            # Определение формата передачи параметров в обработчик
            sig = inspect.signature(handler)
            if "task" in sig.parameters and len(sig.parameters) == 1:
                args = (task,)
                kwargs: Dict[str, Any] = {}
            else:
                args = ()
                kwargs = task.payload

            # Поддержка асинхронных и синхронных функций (через asyncio.to_thread)
            if inspect.iscoroutinefunction(handler):
                result = await handler(*args, **kwargs)
            else:
                result = await asyncio.to_thread(handler, *args, **kwargs)

            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_1,
                status=ExecutionStatus.SUCCESS,
                output=result,
                latency_ms=latency_ms,
            )

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_1,
                status=ExecutionStatus.FAILURE,
                output=None,
                latency_ms=latency_ms,
                error_message=f"Исключение при выполнении '{skill_name}': {type(exc).__name__}: {str(exc)}",
            )
