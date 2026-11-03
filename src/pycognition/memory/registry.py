# Version: 0.1.0 | Release Date: 2026-11-03
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from pycognition.core.system1 import BaseSystem1
from pycognition.schemas import SkillSignature


class SkillRegistryError(Exception):
    """Базовое исключение подсистемы реестра навыков."""


class SkillRegistry:
    """
    Реестр процедурной памяти:
    Управляет сохранением, метаданными, обнаружением на диске и динамической
    загрузкой Python-скриптов в runtime Системы 1 (ProceduralRunner).
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        runner: Optional[BaseSystem1] = None,
    ) -> None:
        self.storage_dir = (
            storage_dir
            if storage_dir is not None
            else Path("src/pycognition/skills/generated").resolve()
        )
        self.runner = runner
        self._signatures: Dict[str, SkillSignature] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}

    @property
    def registered_skills(self) -> List[str]:
        """Возвращает список имен всех загруженных навыков."""
        return list(self._signatures.keys())

    def get_signature(self, skill_name: str) -> Optional[SkillSignature]:
        """Возвращает сигнатуру зарегистрированного навыка."""
        return self._signatures.get(skill_name)

    def save_skill_artifacts(
        self,
        signature: SkillSignature,
        code: str,
        tests_code: Optional[str] = None,
    ) -> Tuple[Path, Path]:
        """
        Сохраняет исходный код функции, ее метаданные и сопутствующие тесты на диск.
        """
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        module_path = self.storage_dir / f"{signature.name}.py"
        meta_path = self.storage_dir / f"{signature.name}.meta.json"

        module_path.write_text(code, encoding="utf-8")
        meta_path.write_text(
            signature.model_dump_json(indent=2),
            encoding="utf-8",
        )

        if tests_code:
            test_path = self.storage_dir / f"test_{signature.name}.py"
            test_path.write_text(tests_code, encoding="utf-8")

        return module_path, meta_path

    def load_skill_from_file(
        self,
        file_path: Path,
        runner: Optional[BaseSystem1] = None,
    ) -> Tuple[SkillSignature, Callable[..., Any]]:
        """
        Динамически импортирует модуль из .py-файла через importlib.util,
        извлекает целевую функцию и регистрирует ее в реестре и инстансе runner.
        """
        if not file_path.is_file():
            raise SkillRegistryError(f"Файл навыка не найден: {file_path}")

        skill_name = file_path.stem
        module_name = f"pycognition.dynamic.{skill_name}"

        # 1. Загрузка метаданных (из .meta.json или fallback по аннотациям)
        meta_path = file_path.with_suffix(".meta.json")
        if meta_path.is_file():
            try:
                meta_dict = json.loads(meta_path.read_text(encoding="utf-8"))
                signature = SkillSignature.model_validate(meta_dict)
            except Exception as exc:
                raise SkillRegistryError(
                    f"Ошибка чтения метаданных {meta_path}: {str(exc)}"
                ) from exc
        else:
            signature = SkillSignature(
                name=skill_name,
                description=f"Динамически загруженный навык {skill_name}",
            )

        # 2. Динамический импорт через importlib.util
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise SkillRegistryError(
                    f"Не удалось построить спецификацию импорта для {file_path}"
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise SkillRegistryError(
                f"Ошибка выполнения импорта модуля '{module_name}': {type(exc).__name__}: {str(exc)}"
            ) from exc

        # 3. Поиск целевой функции
        if not hasattr(module, signature.name):
            sys.modules.pop(module_name, None)
            raise SkillRegistryError(
                f"В модуле {file_path.name} отсутствует функция '{signature.name}'"
            )

        handler = getattr(module, signature.name)
        if not callable(handler):
            sys.modules.pop(module_name, None)
            raise SkillRegistryError(
                f"Объект '{signature.name}' в {file_path.name} не является вызываемым (callable)"
            )

        # 4. Сохранение во внутреннем состоянии
        self._signatures[signature.name] = signature
        self._handlers[signature.name] = handler

        # 5. Регистрация в исполнителе Системы 1
        target_runner = runner or self.runner
        if target_runner is not None:
            target_runner.register_skill(signature, handler)

        return signature, handler

    def load_all_skills(
        self,
        runner: Optional[BaseSystem1] = None,
    ) -> Dict[str, SkillSignature]:
        """
        Сканирует директорию storage_dir, импортирует все .py файлы
        (пропуская тесты и файлы инициализации) и регистрирует их.
        """
        if not self.storage_dir.exists():
            return {}

        loaded: Dict[str, SkillSignature] = {}
        target_runner = runner or self.runner

        for file_path in self.storage_dir.glob("*.py"):
            if file_path.name.startswith(("test_", "__")):
                continue

            try:
                sig, _ = self.load_skill_from_file(file_path, runner=target_runner)
                loaded[sig.name] = sig
            except SkillRegistryError:
                # Пропуск некорректных скриптов с изоляцией сбоя загрузки
                continue

        return loaded
