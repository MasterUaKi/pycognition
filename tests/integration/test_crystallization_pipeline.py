# Version: 0.1.0 | Release Date: 2026-11-03
from pathlib import Path
from unittest.mock import AsyncMock
import pytest

from pycognition.engine.llm_deliberator import LLMDeliberator
from pycognition.engine.meta_arbiter import MetaArbiter
from pycognition.engine.procedural_runner import ProceduralRunner
from pycognition.engine.runtime import CognitiveRuntime
from pycognition.engine.skill_crystallizer import SkillCrystallizer
from pycognition.memory.registry import SkillRegistry
from pycognition.memory.vector_store import VectorStoreMemory
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    ExecutionStatus,
    SkillSignature,
    Task,
)


@pytest.fixture
def test_environment(tmp_path: Path):
    storage_dir = tmp_path / "skills_repo"
    storage_dir.mkdir(parents=True, exist_ok=True)

    memory = VectorStoreMemory()
    runner = ProceduralRunner()
    registry = SkillRegistry(storage_dir=storage_dir, runner=runner)
    crystallizer = SkillCrystallizer(storage_dir=storage_dir)
    arbiter = MetaArbiter(memory=memory, confidence_threshold=0.60)

    # Имитация Системы 2 (LLMDeliberator)
    deliberator = AsyncMock(spec=LLMDeliberator)

    runtime = CognitiveRuntime(
        arbiter=arbiter,
        system1=runner,
        system2=deliberator,
        memory=memory,
        auto_crystallize=False,  # Шаг кристаллизации контролируется вручную в тесте
    )

    return {
        "runtime": runtime,
        "deliberator": deliberator,
        "crystallizer": crystallizer,
        "registry": registry,
        "memory": memory,
        "runner": runner,
        "arbiter": arbiter,
    }


@pytest.mark.asyncio
async def test_full_cognitive_lifecycle(test_environment):
    env = test_environment
    runtime: CognitiveRuntime = env["runtime"]
    deliberator: AsyncMock = env["deliberator"]
    crystallizer: SkillCrystallizer = env["crystallizer"]
    registry: SkillRegistry = env["registry"]
    memory: VectorStoreMemory = env["memory"]
    runner: ProceduralRunner = env["runner"]

    task_1 = Task(
        prompt="calculate hypotenuse right triangle",
        payload={"a": 3.0, "b": 4.0},
    )

    # 1. Первый запуск: навык отсутствует
    deliberator.deliberate.return_value = ExecutionResult(
        task_id=task_1.id,
        track_used=CognitiveTrack.SYSTEM_2,
        status=ExecutionStatus.SUCCESS,
        output=5.0,
        latency_ms=850.0,
        token_usage={"total_tokens": 120},
    )

    result_1 = await runtime.run(task_1)

    assert result_1.track_used == CognitiveTrack.SYSTEM_2
    assert result_1.output == 5.0
    deliberator.deliberate.assert_awaited_once()

    # 2. Моделирование кристаллизации навыка Системой 2
    signature = SkillSignature(
        name="calculate_hypotenuse",
        description="calculate hypotenuse right triangle from sides a and b",
        parameters_schema={"a": "float", "b": "float"},
        return_schema={"result": "float"},
    )

    code = """
import math

def calculate_hypotenuse(a: float, b: float) -> float:
    return math.sqrt(a**2 + b**2)
"""

    tests_code = """
from calculate_hypotenuse import calculate_hypotenuse

def test_hypotenuse_basic():
    assert calculate_hypotenuse(3.0, 4.0) == 5.0
    assert calculate_hypotenuse(5.0, 12.0) == 13.0
"""

    # 3. Валидация через SkillCrystallizer
    cryst_result = await crystallizer.crystallize(
        signature=signature,
        code=code,
        tests_code=tests_code,
    )
    assert cryst_result.success is True
    assert cryst_result.skill_path is not None

    # 4. Регистрация в реестре и процедурной памяти
    registry.load_skill_from_file(cryst_result.skill_path)
    assert runner.has_skill("calculate_hypotenuse") is True

    # 5. Сохранение сигнатуры в VectorStoreMemory для арбитра
    await memory.save_skill_code(signature, code, tests_code)

    # 6. Второй запуск: повторяющаяся задача
    task_2 = Task(
        prompt="calculate hypotenuse right triangle",
        payload={"a": 6.0, "b": 8.0},
    )

    deliberator.deliberate.reset_mock()
    result_2 = await runtime.run(task_2)

    # Задача должна быть перехвачена Системой 1
    assert result_2.track_used == CognitiveTrack.SYSTEM_1
    assert result_2.status == ExecutionStatus.SUCCESS
    assert result_2.output == 10.0
    assert result_2.latency_ms < 50.0  # Локальное быстрое исполнение
    assert result_2.token_usage is None  # Нулевой расход токенов

    # Система 2 не должна вызываться повторно
    deliberator.deliberate.assert_not_awaited()
