# File: src/pycognition/engine/skill_crystallizer.py
# Version: 0.4.1 | Release Date: 2026-11-09
import ast
import builtins
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pycognition.schemas import SkillCapability

logger = logging.getLogger("pycognition.SkillCrystallizer")

CAPABILITY_IMPORT_ALLOWLIST: Dict[SkillCapability, Set[str]] = {
    SkillCapability.PURE_COMPUTATION: {"math", "decimal", "fractions", "statistics"},
    SkillCapability.DATA_TRANSFORMATION: {"math", "json", "re", "datetime", "typing", "collections", "itertools"},
    SkillCapability.DATA_EXTRACTOR: {"bs4", "re", "json", "urllib", "datetime", "typing", "collections", "html"},
    SkillCapability.GENERAL: set(),
}


class ASTSecurityValidator(ast.NodeVisitor):
    def __init__(self, expected_function_name: str, capability: SkillCapability = SkillCapability.GENERAL):
        self.expected_function_name = expected_function_name
        self.capability = capability
        self.allowed_imports = CAPABILITY_IMPORT_ALLOWLIST.get(capability, set())
        self.errors: List[str] = []
        self.found_expected_function = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.expected_function_name:
            self.found_expected_function = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == self.expected_function_name:
            self.found_expected_function = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            root_pkg = alias.name.split(".")[0]
            if root_pkg not in self.allowed_imports:
                self.errors.append(f"Импорт модуля '{alias.name}' запрещен для профиля {self.capability.name}.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            root_pkg = node.module.split(".")[0]
            if root_pkg not in self.allowed_imports:
                self.errors.append(f"Импорт из модуля '{node.module}' запрещен для профиля {self.capability.name}.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "compile", "open"}:
                self.errors.append(f"Вызов функции '{node.func.id}' запрещен правилами песочницы.")
        self.generic_visit(node)


class SkillCrystallizer:
    def __init__(self, storage_dir: Path | str):
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def validate_ast(
        self,
        code: str,
        expected_function_name: str,
        capability: SkillCapability = SkillCapability.GENERAL
    ) -> Tuple[bool, Optional[str]]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Синтаксическая ошибка в коде: {e.msg} (строка {e.lineno})"

        validator = ASTSecurityValidator(expected_function_name, capability)
        validator.visit(tree)

        if not validator.found_expected_function:
            return False, f"Функция '{expected_function_name}' не найдена в теле синтезированного кода."

        if validator.errors:
            return False, "; ".join(validator.errors)

        return True, None

    def dry_run_skill(
        self,
        code: str,
        func_name: str,
        args: tuple = ()
    ) -> Tuple[bool, Any, Optional[str]]:
        # Передаем реальный builtins словарь с сохранением __import__
        safe_builtins = builtins.__dict__.copy()

        # Блокируем только опасные системные вызовы
        for dangerous_op in ("eval", "exec", "compile", "open", "breakpoint"):
            safe_builtins.pop(dangerous_op, None)

        safe_globals: Dict[str, Any] = {
            "__builtins__": safe_builtins
        }
        local_scope: Dict[str, Any] = {}

        try:
            compiled_code = compile(code, f"<sandbox_{func_name}>", "exec")
            exec(compiled_code, safe_globals, local_scope)

            func = local_scope.get(func_name)
            if not callable(func):
                return False, None, f"Объект '{func_name}' не является вызываемой функцией."

            result = func(*args)
            return True, result, None
        except Exception as err:
            return False, None, f"Исключение при тестовом прогоне: {type(err).__name__} - {err}"

    def crystallize_with_regression_guard(
        self,
        code: str,
        func_name: str,
        capability: SkillCapability,
        test_args: Optional[tuple] = None,
        baseline_yield: int = 0
    ) -> Tuple[bool, str, int]:
        ok, err = self.validate_ast(code, func_name, capability)
        if not ok:
            return False, f"AST отклонен: {err}", 0

        measured_yield = 0

        if test_args is not None:
            exec_ok, result, exec_err = self.dry_run_skill(code, func_name, test_args)
            if not exec_ok:
                return False, f"Сбой тестового прогона: {exec_err}", 0

            if isinstance(result, list):
                measured_yield = len(result)
            elif result is not None:
                measured_yield = 1

            # Жесткий барьер: экстрактор с выходом 0 никогда не кристаллизуется
            if capability == SkillCapability.DATA_EXTRACTOR and measured_yield == 0:
                return False, "Экстрактор вернул 0 программ. Сохранение пустых навыков запрещено.", 0

            if baseline_yield > 0 and measured_yield < baseline_yield:
                return (
                    False,
                    f"Регрессия навыка: кандидат извлек {measured_yield} объектов, "
                    f"тогда как базовый навык дает {baseline_yield}.",
                    measured_yield
                )

        target_file = self.storage_dir / f"{func_name}.py"
        target_file.write_text(code, encoding="utf-8")
        logger.info(f"Навык '{func_name}' успешно кристаллизован (выход: {measured_yield}).")

        return True, "Успешно кристаллизован", measured_yield
