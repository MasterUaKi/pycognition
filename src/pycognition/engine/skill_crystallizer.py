# Version: 0.2.1 | Release Date: 2026-11-09
import ast
import asyncio
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import tempfile
from typing import List, Optional, Set, Tuple

from pycognition.schemas import SkillCapability, SkillSignature


@dataclass
class CrystallizationResult:
    """Результат валидации, тестирования и сохранения навыка."""
    success: bool
    skill_path: Optional[Path] = None
    tests_path: Optional[Path] = None
    error_message: Optional[str] = None
    stdout: Optional[str] = None


class ASTSecurityValidator(ast.NodeVisitor):
    """
    Инспектор абстрактного синтаксического дерева (AST) на основе профилей разрешений.
    
    1. Жестко блокирует деструктивные системные вызовы во всех профилях.
    2. Разрешает безопасные библиотеки парсинга и сетевого I/O в зависимости от SkillCapability.
    3. Контролирует присутствие целевой сигнатуры функции.
    """

    CORE_BANNED_IMPORTS: Set[str] = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "pty",
        "importlib",
        "ctypes",
        "multiprocessing",
        "threading",
    }

    CORE_BANNED_FUNCTIONS: Set[str] = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "globals",
        "locals",
        "breakpoint",
    }

    PARSER_ALLOWED_ROOTS: Set[str] = {
        "bs4",
        "beautifulsoup4",
        "selectolax",
        "lxml",
        "xml",
        "json",
        "csv",
        "re",
        "html",
        "urllib",
    }

    NETWORK_ALLOWED_ROOTS: Set[str] = {
        "httpx",
        "urllib",
        "http",
    }

    SAFE_STANDARD_ROOTS: Set[str] = {
        "math",
        "statistics",
        "datetime",
        "typing",
        "collections",
        "itertools",
        "functools",
        "pydantic",
        "dataclasses",
        "enum",
        "uuid",
        "decimal",
        "fractions",
        "copy",
        "string",
    }

    def __init__(
        self,
        expected_function_name: str,
        capability: SkillCapability = SkillCapability.COMPUTATIONAL,
        allowed_domains: Optional[List[str]] = None,
    ) -> None:
        self.expected_function_name = expected_function_name
        self.capability = capability
        self.allowed_domains = allowed_domains or []
        self.found_target_function = False
        self.violations: List[str] = []

    def _check_import_allowed(self, module_name: str, lineno: int) -> None:
        root_module = module_name.split(".")[0]

        # 1. Безусловный запрет деструктивных системных пакетов
        if root_module in self.CORE_BANNED_IMPORTS:
            self.violations.append(
                f"Запрещенный импорт модуля '{module_name}' (строка {lineno})"
            )
            return

        # 2. Профиль COMPUTATIONAL: запрещены любые I/O и сетевые библиотеки
        if self.capability == SkillCapability.COMPUTATIONAL:
            network_io_modules = {"socket", "httpx", "urllib", "http", "requests", "aiohttp"}
            if root_module in network_io_modules:
                self.violations.append(
                    f"Запрещенный импорт модуля '{module_name}' (строка {lineno})"
                )
            return

        # 3. Профиль DATA_EXTRACTOR: низкоуровневые сокеты запрещены
        if self.capability == SkillCapability.DATA_EXTRACTOR:
            raw_socket_modules = {"socket", "requests", "aiohttp"}
            if root_module in raw_socket_modules:
                self.violations.append(
                    f"Запрещенный импорт модуля '{module_name}' (строка {lineno})"
                )
            return

        # 4. Профиль NETWORK_CONNECTOR: разрешен httpx, но socket/pty запрещен
        if self.capability == SkillCapability.NETWORK_CONNECTOR:
            if root_module in {"socket", "pty"}:
                self.violations.append(
                    f"Запрещенный импорт модуля '{module_name}' (строка {lineno})"
                )
            return

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._check_import_allowed(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._check_import_allowed(node.module, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in self.CORE_BANNED_FUNCTIONS:
                self.violations.append(
                    f"Запрещенный вызов функции '{node.func.id}()' (строка {node.lineno})"
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name == self.expected_function_name:
            self.found_target_function = True
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node.name == self.expected_function_name:
            self.found_target_function = True
        self.generic_visit(node)


class SkillCrystallizer:
    """
    Конвейер кристаллизации навыков с поддержкой профилей возможностей.
    """

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        self.storage_dir = (
            storage_dir
            if storage_dir is not None
            else Path("src/pycognition/skills/generated").resolve()
        )

    def validate_ast(
        self,
        code: str,
        expected_function_name: str,
        capability: SkillCapability = SkillCapability.COMPUTATIONAL,
        allowed_domains: Optional[List[str]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Проверяет синтаксис и безопасность Python-кода по профилю прав."""
        try:
            tree = ast.parse(code)
        except SyntaxError as err:
            return False, f"Синтаксическая ошибка в коде: {err.msg} (строка {err.lineno})"

        validator = ASTSecurityValidator(
            expected_function_name=expected_function_name,
            capability=capability,
            allowed_domains=allowed_domains,
        )
        validator.visit(tree)

        if validator.violations:
            return False, f"Нарушения безопасности AST: {'; '.join(validator.violations)}"

        if not validator.found_target_function:
            return (
                False,
                f"В коде отсутствует целевая функция '{expected_function_name}'",
            )

        return True, None

    async def run_sandbox_tests(
        self,
        skill_name: str,
        code: str,
        tests_code: str,
        timeout: float = 15.0,
    ) -> Tuple[bool, str]:
        """Запускает модульные тесты через subprocess с pytest в песочнице."""
        # ignore_cleanup_errors=True предотвращает сбои WinError 32 при удалении временных папок в Windows
        with tempfile.TemporaryDirectory(prefix="pycognition_sandbox_", ignore_cleanup_errors=True) as tmp_dir:
            tmp_path = Path(tmp_dir)
            module_file = tmp_path / f"{skill_name}.py"
            test_file = tmp_path / f"test_{skill_name}.py"

            module_file.write_text(code, encoding="utf-8")
            test_file.write_text(tests_code, encoding="utf-8")

            env = os.environ.copy()
            current_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                f"{tmp_path};{current_pythonpath}" if sys.platform == "win32" and current_pythonpath
                else f"{tmp_path}:{current_pythonpath}" if current_pythonpath
                else str(tmp_path)
            )

            cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-v",
                "--tb=short",
            ]

            proc = None
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(tmp_path),
                    env=env,
                )

                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )

                stdout_str = stdout_bytes.decode("utf-8", errors="replace")
                stderr_str = stderr_bytes.decode("utf-8", errors="replace")
                full_output = f"{stdout_str}\n{stderr_str}".strip()

                if proc.returncode == 0:
                    return True, full_output
                return False, f"Тесты pytest завершились с ошибкой (код {proc.returncode}):\n{full_output}"

            except asyncio.TimeoutError:
                if proc is not None:
                    try:
                        proc.kill()
                        await proc.wait()  # Корректное освобождение дескрипторов в Windows
                    except Exception:
                        pass
                await asyncio.sleep(0.1)
                return False, f"Превышен таймаут выполнения тестов в песочнице ({timeout} сек)."
            except Exception as exc:
                return False, f"Ошибка запуска песочницы: {type(exc).__name__}: {str(exc)}"

    async def crystallize(
        self,
        signature: SkillSignature,
        code: str,
        tests_code: str,
        timeout: float = 15.0,
    ) -> CrystallizationResult:
        """Полный цикл кристаллизации с учетом capability-профиля подписи."""
        # 1. Валидация AST с учетом прав
        ast_ok, ast_error = self.validate_ast(
            code=code,
            expected_function_name=signature.name,
            capability=signature.capability,
            allowed_domains=signature.allowed_domains,
        )
        if not ast_ok:
            return CrystallizationResult(success=False, error_message=ast_error)

        # 2. Исполнение тестов в изолированном окружении
        tests_ok, tests_output = await self.run_sandbox_tests(
            skill_name=signature.name,
            code=code,
            tests_code=tests_code,
            timeout=timeout,
        )
        if not tests_ok:
            return CrystallizationResult(
                success=False,
                error_message=tests_output,
                stdout=tests_output,
            )

        # 3. Фиксация на диске
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            skill_path = self.storage_dir / f"{signature.name}.py"
            tests_path = self.storage_dir / f"test_{signature.name}.py"

            skill_path.write_text(code, encoding="utf-8")
            tests_path.write_text(tests_code, encoding="utf-8")

            return CrystallizationResult(
                success=True,
                skill_path=skill_path,
                tests_path=tests_path,
                stdout=tests_output,
            )
        except OSError as exc:
            return CrystallizationResult(
                success=False,
                error_message=f"Ошибка сохранения навыка на диск: {str(exc)}",
                stdout=tests_output,
            )