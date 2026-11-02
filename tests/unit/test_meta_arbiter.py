# Version: 0.1.0 | Release Date: 2026-11-02
from typing import Optional, Tuple
import pytest
from pycognition.core.memory import BaseMemory
from pycognition.engine.meta_arbiter import MetaArbiter
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    SkillSignature,
    Task,
)


class MockMemory(BaseMemory):
    """Тестовая реализация памяти с контролируемым поведением."""

    def __init__(self, match_result: Optional[Tuple[SkillSignature, float]] = None) -> None:
        self.match_result = match_result
        self.saved_skills: list[str] = []
        self.execution_logs: list[ExecutionResult] = []

    async def save_skill_code(self, signature: SkillSignature, code: str, tests: str) -> None:
        self.saved_skills.append(signature.name)

    async def find_matching_skill(self, task: Task) -> Optional[Tuple[SkillSignature, float]]:
        return self.match_result

    async def log_execution(self, task: Task, result: ExecutionResult) -> None:
        self.execution_logs.append(result)


@pytest.fixture
def sample_skill() -> SkillSignature:
    return SkillSignature(
        name="sort_list",
        description="Сортировка списка элементов",
    )


def test_confidence_threshold_validation() -> None:
    arbiter = MetaArbiter()
    assert arbiter.confidence_threshold == 0.75

    arbiter.set_confidence_threshold(0.9)
    assert arbiter.confidence_threshold == 0.9

    with pytest.raises(ValueError, match=r"\[0.0, 1.0\]"):
        arbiter.set_confidence_threshold(1.5)

    with pytest.raises(ValueError, match=r"\[0.0, 1.0\]"):
        arbiter.set_confidence_threshold(-0.1)


@pytest.mark.asyncio
async def test_route_to_system2_without_memory() -> None:
    arbiter = MetaArbiter(memory=None)
    task = Task(prompt="Напиши научную статью по ИИ")

    decision = await arbiter.route(task)

    assert decision.selected_track == CognitiveTrack.SYSTEM_2
    assert decision.confidence_score == 0.0
    assert decision.matched_skill is None
    assert "Система 2" in decision.reasoning


@pytest.mark.asyncio
async def test_route_to_system1_explicit_metadata(sample_skill: SkillSignature) -> None:
    arbiter = MetaArbiter(memory=None, confidence_threshold=0.8)
    task = Task(
        prompt="Отсортируй массив",
        metadata={"target_skill": sample_skill},
    )

    decision = await arbiter.route(task)

    assert decision.selected_track == CognitiveTrack.SYSTEM_1
    assert decision.confidence_score == 1.0
    assert decision.matched_skill == sample_skill


@pytest.mark.asyncio
async def test_route_to_system1_with_high_memory_confidence(
    sample_skill: SkillSignature,
) -> None:
    mock_memory = MockMemory(match_result=(sample_skill, 0.92))
    arbiter = MetaArbiter(memory=mock_memory, confidence_threshold=0.80)
    task = Task(prompt="Сортировка списка")

    decision = await arbiter.route(task)

    assert decision.selected_track == CognitiveTrack.SYSTEM_1
    assert decision.confidence_score == 0.92
    assert decision.matched_skill == sample_skill
    assert "Система 1" in decision.reasoning


@pytest.mark.asyncio
async def test_route_to_system2_with_low_memory_confidence(
    sample_skill: SkillSignature,
) -> None:
    mock_memory = MockMemory(match_result=(sample_skill, 0.65))
    arbiter = MetaArbiter(memory=mock_memory, confidence_threshold=0.80)
    task = Task(prompt="Сложная нетривиальная сортировка с условием")

    decision = await arbiter.route(task)

    assert decision.selected_track == CognitiveTrack.SYSTEM_2
    assert decision.confidence_score == 0.65
    assert decision.matched_skill is None
    assert "Система 2" in decision.reasoning
