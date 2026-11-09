#!/usr/bin/env python3
# Version: 1.0.0 | Release Date: 2026-11-09
"""Автономный инспектор структуры проекта pycognition.

Сканирует дерево каталогов, отсекает виртуальные окружения и кэш,
собирает размеры файлов и выводит классы/функции из python-модулей.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import sys

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "preprints_pdf",
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".DS_Store",
}


def inspect_python_file(path: Path) -> list[str]:
    """Извлекает имена классов и функций верхнего уровня через AST."""
    details: list[str] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                details.append(f"class {node.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                details.append(f"{prefix} {node.name}()")
    except Exception as exc:
        details.append(f"<ошибка парсинга AST: {exc}>")
    return details


def generate_tree(root_dir: Path) -> list[str]:
    """Строит текстовое дерево каталогов и собирает метаданные."""
    lines: list[str] = [f"Корень проекта: {root_dir.resolve()}", ""]
    py_files_summary: list[tuple[Path, list[str]]] = []

    for root, dirs, files in os.walk(root_dir):
        # Модифицируем dirs in-place, чтобы os.walk не заходил в игнорируемые папки
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS and not d.endswith(".egg-info")])

        current_path = Path(root)
        rel_path = current_path.relative_to(root_dir)
        depth = len(rel_path.parts)

        if depth > 0:
            indent = "  " * (depth - 1)
            lines.append(f"{indent}📁 {current_path.name}/")

        filtered_files = sorted(
            [f for f in files if Path(f).suffix not in IGNORE_EXTENSIONS and f != "inspect_project.py"]
        )

        file_indent = "  " * depth
        for file in filtered_files:
            file_path = current_path / file
            try:
                size_kb = file_path.stat().st_size / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb >= 1 else f"{file_path.stat().st_size} B"
            except OSError:
                size_str = "unknown"

            lines.append(f"{file_indent}📄 {file} ({size_str})")

            if file.endswith(".py"):
                symbols = inspect_python_file(file_path)
                py_files_summary.append((file_path.relative_to(root_dir), symbols))

    lines.append("\n" + "=" * 70)
    lines.append("СОСТАВ PYTHON-МОДУЛЕЙ (КЛАССЫ И ФУНКЦИИ ВЕРХНЕГО УРОВНЯ):")
    lines.append("=" * 70)

    for rel_py_path, symbols in py_files_summary:
        lines.append(f"\nМодуль: {rel_py_path}")
        if symbols:
            for sym in symbols:
                lines.append(f"    • {sym}")
        else:
            lines.append("    (нет классов или функций верхнего уровня / скрипт / пустой)")

    return lines


def main() -> None:
    root_dir = Path(".").resolve()
    output_file = root_dir / "project_structure.txt"

    report_lines = generate_tree(root_dir)
    full_report = "\n".join(report_lines)

    # Запись в файл
    output_file.write_text(full_report, encoding="utf-8")

    # Дублирование в stdout
    print(full_report)
    print("\n" + "=" * 70)
    print(f"Отчет успешно сохранен в файл: {output_file.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()