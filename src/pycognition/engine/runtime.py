# Version: 0.1.0 | Release Date: 2026-11-02
from pycognition.core.arbiter import BaseArbiter
from pycognition.core.memory import BaseMemory
from pycognition.core.system1 import BaseSystem1
from pycognition.core.system2 import BaseSystem2
from pycognition.schemas import CognitiveTrack, ExecutionResult, ExecutionStatus, Task


class CognitiveRuntime:
    """
    Центральный координатор pycognition:
    Связывает Арбитр, Систему 1, Систему 2 и Память в единый цикл выполнения и обучения.
    """

    def __init__(
        self,
        arbiter: BaseArbiter,
        system1: BaseSystem1,
        system2: BaseSystem2,
        memory: BaseMemory,
        auto_crystallize: bool = True,
    ) -> None:
        self.arbiter = arbiter
        self.system1 = system1
        self.system2 = system2
        self.memory = memory
        self.auto_crystallize = auto_crystallize

    async def run(self, task: Task) -> ExecutionResult:
        """
        Выполняет сквозную обработку задачи через когнитивную маршрутизацию.
        """
        decision = await self.arbiter.route(task)

        # 1. Попытка быстрого исполнения через Систему 1
        if decision.selected_track == CognitiveTrack.SYSTEM_1 and decision.matched_skill:
            result = await self.system1.execute(decision.matched_skill.name, task)
            if result.status == ExecutionStatus.SUCCESS:
                await self.memory.log_execution(task, result)
                return result
            # Если процедурный скрипт завершился ошибкой, передаем задачу в Систему 2
            task.metadata["system1_fallback_cause"] = result.error_message

        # 2. Делиберативное решение через Систему 2 (LLM)
        deliberation_result = await self.system2.deliberate(task)
        await self.memory.log_execution(task, deliberation_result)

        # 3. Кристаллизация нового навыка при успешном исходе
        if self.auto_crystallize and deliberation_result.status == ExecutionStatus.SUCCESS:
            await self.system2.synthesize_skill(
                task=task,
                solution_context=str(deliberation_result.output),
            )

        return deliberation_result
