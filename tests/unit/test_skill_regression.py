# Version: 0.3.0 | Release Date: 2026-11-09
from pathlib import Path
import pytest
from pycognition.engine.skill_crystallizer import SkillCrystallizer
from pycognition.schemas import SkillCapability


def test_regression_guard_blocks_degraded_code(tmp_path: Path):
    crystallizer = SkillCrystallizer(storage_dir=tmp_path)
    func_name = "test_extractor"

    # Скрипт-кандидат возвращает пустой список
    empty_code = f"""def {func_name}(html, base_url):
    return []
"""

    # Пытаемся перезаписать навык с базовым выходом 15 объектов
    success, msg, yld = crystallizer.crystallize_with_regression_guard(
        code=empty_code,
        func_name=func_name,
        capability=SkillCapability.DATA_EXTRACTOR,
        test_args=("<html></html>", "https://example.com"),
        baseline_yield=15
    )

    assert not success
    assert "Регрессия навыка" in msg
    assert not (tmp_path / f"{func_name}.py").exists()


def test_regression_guard_allows_improved_code(tmp_path: Path):
    crystallizer = SkillCrystallizer(storage_dir=tmp_path)
    func_name = "test_extractor"

    good_code = f"""def {func_name}(html, base_url):
    return [{{"title": "Grant 1"}}, {{"title": "Grant 2"}}]
"""

    success, msg, yld = crystallizer.crystallize_with_regression_guard(
        code=good_code,
        func_name=func_name,
        capability=SkillCapability.DATA_EXTRACTOR,
        test_args=("<html></html>", "https://example.com"),
        baseline_yield=1
    )

    assert success
    assert yld == 2
    assert (tmp_path / f"{func_name}.py").exists()