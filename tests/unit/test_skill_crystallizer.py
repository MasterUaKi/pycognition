# Version: 0.1.0 | Release Date: 2026-11-02
from pathlib import Path
import pytest

from pycognition.engine.skill_crystallizer import SkillCrystallizer
from pycognition.schemas import SkillSignature


@pytest.fixture
def crystallizer(tmp_path: Path) -> SkillCrystallizer:
    storage = tmp_path / "skills"
    return SkillCrystallizer(storage_dir=storage)


@pytest.fixture
def valid_signature() -> SkillSignature:
    return SkillSignature(
        name="fibonacci",
        description="Вычисление n-го числа Фибоначчи",
    )


VALID_CODE = """
def fibonacci(n: int) -> int:
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
"""

VALID_TESTS = """
from fibonacci import fibonacci

def test_fibonacci_base():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
"""


def test_validate_ast_success(crystallizer: SkillCrystallizer) -> None:
    ok, error = crystallizer.validate_ast(VALID_CODE, "fibonacci")
    assert ok is True
    assert error is None


def test_validate_ast_syntax_error(crystallizer: SkillCrystallizer) -> None:
    bad_code = "def fibonacci(n) return n"
    ok, error = crystallizer.validate_ast(bad_code, "fibonacci")
    assert ok is False
    assert "Синтаксическая ошибка" in str(error)


def test_validate_ast_missing_function(crystallizer: SkillCrystallizer) -> None:
    other_code = "def calculate_sum(a, b): return a + b"
    ok, error = crystallizer.validate_ast(other_code, "fibonacci")
    assert ok is False
    assert "отсутствует целевая функция 'fibonacci'" in str(error)


def test_validate_ast_banned_import(crystallizer: SkillCrystallizer) -> None:
    unsafe_code = """
import os
def fibonacci(n: int) -> int:
    return n
"""
    ok, error = crystallizer.validate_ast(unsafe_code, "fibonacci")
    assert ok is False
    assert "Запрещенный импорт модуля 'os'" in str(error)


def test_validate_ast_banned_function(crystallizer: SkillCrystallizer) -> None:
    unsafe_code = """
def fibonacci(n: int) -> int:
    eval("print('danger')")
    return n
"""
    ok, error = crystallizer.validate_ast(unsafe_code, "fibonacci")
    assert ok is False
    assert "Запрещенный вызов функции 'eval()'" in str(error)


@pytest.mark.asyncio
async def test_run_sandbox_tests_success(crystallizer: SkillCrystallizer) -> None:
    ok, output = await crystallizer.run_sandbox_tests(
        skill_name="fibonacci",
        code=VALID_CODE,
        tests_code=VALID_TESTS,
    )
    assert ok is True
    assert "passed" in output


@pytest.mark.asyncio
async def test_run_sandbox_tests_failure(crystallizer: SkillCrystallizer) -> None:
    failing_tests = """
from fibonacci import fibonacci

def test_fibonacci_wrong_assertion():
    assert fibonacci(5) == 999
"""
    ok, output = await crystallizer.run_sandbox_tests(
        skill_name="fibonacci",
        code=VALID_CODE,
        tests_code=failing_tests,
    )
    assert ok is False
    assert "FAILED" in output


@pytest.mark.asyncio
async def test_run_sandbox_tests_timeout(crystallizer: SkillCrystallizer) -> None:
    infinite_loop_code = """
def fibonacci(n: int) -> int:
    while True:
        pass
    return n
"""
    ok, output = await crystallizer.run_sandbox_tests(
        skill_name="fibonacci",
        code=infinite_loop_code,
        tests_code=VALID_TESTS,
        timeout=1.0,
    )
    assert ok is False
    assert "Превышен таймаут" in output


@pytest.mark.asyncio
async def test_crystallize_full_cycle(
    crystallizer: SkillCrystallizer, valid_signature: SkillSignature
) -> None:
    result = await crystallizer.crystallize(
        signature=valid_signature,
        code=VALID_CODE,
        tests_code=VALID_TESTS,
    )

    assert result.success is True
    assert result.error_message is None
    assert result.skill_path is not None
    assert result.tests_path is not None

    assert result.skill_path.is_file()
    assert result.tests_path.is_file()
    assert result.skill_path.name == "fibonacci.py"
    assert "def fibonacci" in result.skill_path.read_text(encoding="utf-8")
