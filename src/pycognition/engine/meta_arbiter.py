# Version: 0.1.0 | Release Date: 2026-11-02
from typing import Optional

from pycognition.core.arbiter import BaseArbiter
from pycognition.core.memory import BaseMemory
from pycognition.schemas import (
    CognitiveTrack,
    RoutingDecision,
    SkillSignature,
    Task,
)


class MetaArbiter(BaseArbiter):
    """
    Метакогнитивный арбитр: маршрутизирует задачи между Системой 1 и Системой 2.
    Принимает решение на основе сравнения оценки уверенности (confidence score)
    с динамическим пороговым значением theta.
    """

    def __init__(
        self,
        memory: Optional[BaseMemory] = None,
        confidence_threshold: float = 0.75,
    ) -> None:
        self.memory = memory
        self._confidence_threshold = confidence_threshold

    @property
    def confidence_threshold(self) -> float:
        return self._confidence_threshold

    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Устанавливает порог уверенности в диапазоне [0.0, 1.0].
        """
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("Порог уверенности должен находиться в диапазоне [0.0, 1.0]")
        self._confidence_threshold = threshold

    async def route(self, task: Task) -> RoutingDecision:
        """
        Оценивает задачу и определяет целевую когнитивную траекторию.
        """
        matched_skill: Optional[SkillSignature] = None
        confidence = 0.0

        # Поиск совпадений через компонент памяти
        if self.memory is not None:
            match_result = await self.memory.find_matching_skill(task)
            if match_result is not None:
                matched_skill, confidence = match_result
        else:
            # Fallback: явное указание целевого навыка в метаданных задачи
            explicit_skill = task.metadata.get("target_skill")
            if isinstance(explicit_skill, SkillSignature):
                matched_skill = explicit_skill
                confidence = 1.0

        # Решение в пользу Системы 1 при достаточной уверенности
        if matched_skill is not None and confidence >= self._confidence_threshold:
            return RoutingDecision(
                selected_track=CognitiveTrack.SYSTEM_1,
                confidence_score=confidence,
                matched_skill=matched_skill,
                reasoning=(
                    f"Навык '{matched_skill.name}' найден с уверенностью {confidence:.2f} >= "
                    f"{self._confidence_threshold:.2f}. Направление в процедурный контур (Система 1)."
                ),
            )

        # Перенаправление в Систему 2 при новизне или высокой неопределенности
        return RoutingDecision(
            selected_track=CognitiveTrack.SYSTEM_2,
            confidence_score=confidence,
            matched_skill=None,
            reasoning=(
                f"Уверенность ({confidence:.2f}) ниже порога ({self._confidence_threshold:.2f}) "
                "или подходящий процедурный навык отсутствует. "
                "Направление в делиберативный контур рассуждений (Система 2)."
            ),
        )
