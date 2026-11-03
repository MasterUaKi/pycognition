# Version: 0.1.0 | Release Date: 2026-11-03
from pathlib import Path
import pytest

from pycognition.engine.procedural_runner import ProceduralRunner
from pycognition.memory.registry import SkillRegistry, SkillRegistryError
from pycognition.schemas import ExecutionStatus, SkillSignature, Task


@pytest.fixture
def runner() -> ProceduralRunner:
    return ProceduralRunner()


@pytest.fixture
def registry(tmp_path: Path, runner: ProceduralRunner) -> SkillRegistry:
    skills_dir = tmp_path / "skills"
    return SkillRegistry(storage_dir=skills_dir, runner=runner)


@pytest.fixture
def sample_signature() -> SkillSignature:
    return SkillSignature(
        name="multiply_values",
        description="Умножение двух чисел",
        parameters_schema={"x": "int", "y": "int"},
        return_schema={"result": "int"},
    )


SAMPLE_CODE = """
def multiply_values(x: int, y: int) -> int:
    return x * y
"""

SAMPLE_TESTS = """
from multiply_values import multiply_values

def test_multiply():
    assert multiply_values(3, 4) == 12
"""


def test_save_skill_artifacts(
    registry: SkillRegistry,
    sample_signature: SkillSignature,
) -> None:
    mod_path, meta_path = registry.save_skill_artifacts(
        signature=sample_signature,
        code=SAMPLE_CODE,
        tests_code=SAMPLE_TESTS,
    )

    assert mod_path.is_file()
    assert meta_path.is_file()
    assert (registry.storage_dir / "test_multiply_values.py").is_file()
    assert "multiply_values" in meta_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_load_skill_from_file_and_execute(
    registry: SkillRegistry,
    runner: ProceduralRunner,
    sample_signature: SkillSignature,
) -> None:
    mod_path, _ = registry.save_skill_artifacts(
        signature=sample_signature,
        code=SAMPLE_CODE,
    )

    sig, handler = registry.load_skill_from_file(mod_path)

    assert sig.name == "multiply_values"
    assert callable(handler)
    assert runner.has_skill("multiply_values")
    assert registry.get_signature("multiply_values") is not None

    # Проверка сквозного исполнения через зарегистрированный ProceduralRunner
    task = Task(prompt="Умножь 6 на 7", payload={"x": 6, "y": 7})
    result = await runner.execute("multiply_values", task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == 42


def test_load_skill_fallback_signature_without_meta_json(
    registry: SkillRegistry,
    tmp_path: Path,
) -> None:
    raw_file = tmp_path / "raw_skill.py"
    raw_file.write_text(
        "def raw_skill(val: str) -> str:\n    return f'processed_{val}'\n",
        encoding="utf-8",
    )

    sig, _ = registry.load_skill_from_file(raw_file)

    assert sig.name == "raw_skill"
    assert "Динамически загруженный" in sig.description


def test_load_skill_missing_file_raises_error(registry: SkillRegistry) -> None:
    missing_path = registry.storage_dir / "non_existent.py"
    with pytest.raises(SkillRegistryError, match="Файл навыка не найден"):
        registry.load_skill_from_file(missing_path)


def test_load_skill_syntax_error_raises_error(
    registry: SkillRegistry,
    tmp_path: Path,
) -> None:
    broken_file = tmp_path / "broken_syntax.py"
    broken_file.write_text("def broken_syntax(x return x\n", encoding="utf-8")

    with pytest.raises(SkillRegistryError, match="Ошибка выполнения импорта"):
        registry.load_skill_from_file(broken_file)


def test_load_skill_missing_target_callable(
    registry: SkillRegistry,
    tmp_path: Path,
) -> None:
    wrong_file = tmp_path / "target_func.py"
    wrong_file.write_text("def another_func(): pass\n", encoding="utf-8")

    with pytest.raises(SkillRegistryError, match="отсутствует функция 'target_func'"):
        registry.load_skill_from_file(wrong_file)


@pytest.mark.asyncio
async def test_load_all_skills_directory(
    registry: SkillRegistry,
    runner: ProceduralRunner,
) -> None:
    registry.save_skill_artifacts(
        signature=SkillSignature(name="skill_a", description="Skill A"),
        code="def skill_a(n: int) -> int: return n + 1",
    )
    registry.save_skill_artifacts(
        signature=SkillSignature(name="skill_b", description="Skill B"),
        code="def skill_b(n: int) -> int: return n * 2",
    )

    loaded = registry.load_all_skills()

    assert "skill_a" in loaded
    assert "skill_b" in loaded
    assert runner.has_skill("skill_a")
    assert runner.has_skill("skill_b")

    task_a = Task(prompt="Task A", payload={"n": 10})
    res_a = await runner.execute("skill_a", task_a)
    assert res_a.output == 11

    task_b = Task(prompt="Task B", payload={"n": 10})
    res_b = await runner.execute("skill_b", task_b)
    assert res_b.output == 20
