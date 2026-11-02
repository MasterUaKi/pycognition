# Version: 0.1.0 | Release Date: 2026-11-02
import pytest
from pycognition.engine.procedural_runner import ProceduralRunner
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionStatus,
    SkillSignature,
    Task,
)


@pytest.fixture
def runner() -> ProceduralRunner:
    return ProceduralRunner()


@pytest.fixture
def sample_signature() -> SkillSignature:
    return SkillSignature(
        name="sum_numbers",
        description="Вычисляет сумму двух чисел a и b",
        parameters_schema={"a": "int", "b": "int"},
        return_schema={"result": "int"},
    )


def test_register_and_has_skill(
    runner: ProceduralRunner, sample_signature: SkillSignature
) -> None:
    assert not runner.has_skill("sum_numbers")
    runner.register_skill(sample_signature, lambda a, b: a + b)
    assert runner.has_skill("sum_numbers")


@pytest.mark.asyncio
async def test_execute_sync_skill_success(
    runner: ProceduralRunner, sample_signature: SkillSignature
) -> None:
    runner.register_skill(sample_signature, lambda a, b: a + b)
    task = Task(prompt="Сложи 5 и 7", payload={"a": 5, "b": 7})

    result = await runner.execute("sum_numbers", task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.track_used == CognitiveTrack.SYSTEM_1
    assert result.output == 12
    assert result.latency_ms >= 0.0
    assert result.error_message is None


@pytest.mark.asyncio
async def test_execute_async_skill_success(runner: ProceduralRunner) -> None:
    async def async_echo(text: str) -> str:
        return f"echo: {text}"

    sig = SkillSignature(
        name="async_echo",
        description="Асинхронное эхо",
    )
    runner.register_skill(sig, async_echo)
    task = Task(prompt="Эхо тест", payload={"text": "hello"})

    result = await runner.execute("async_echo", task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == "echo: hello"


@pytest.mark.asyncio
async def test_execute_skill_accepting_task_object(runner: ProceduralRunner) -> None:
    def inspect_task(task: Task) -> str:
        return f"Task ID: {task.id}"

    sig = SkillSignature(name="inspect_task", description="Инспекция задачи")
    runner.register_skill(sig, inspect_task)
    task = Task(prompt="Проверь задачу")

    result = await runner.execute("inspect_task", task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == f"Task ID: {task.id}"


@pytest.mark.asyncio
async def test_execute_non_existent_skill(runner: ProceduralRunner) -> None:
    task = Task(prompt="Несуществующий навык")
    result = await runner.execute("missing_skill", task)

    assert result.status == ExecutionStatus.FAILURE
    assert result.output is None
    assert "не зарегистрирован" in str(result.error_message)


@pytest.mark.asyncio
async def test_execute_failing_skill_isolation(runner: ProceduralRunner) -> None:
    def raise_division_by_zero(x: int) -> float:
        return x / 0

    sig = SkillSignature(name="fail_op", description="Сбойная операция")
    runner.register_skill(sig, raise_division_by_zero)
    task = Task(prompt="Деление на ноль", payload={"x": 10})

    result = await runner.execute("fail_op", task)

    assert result.status == ExecutionStatus.FAILURE
    assert result.output is None
    assert "ZeroDivisionError" in str(result.error_message)
