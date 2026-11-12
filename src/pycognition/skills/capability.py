# File: src/pycognition/skills/capability.py
# Version: 1.2.0 | Release Date: 2026-11-12
# EN: Declarative security capability contracts and static AST safety auditor for synthesized skills.
# DE: Deklarative Sicherheits-Capability-Verträge und statischer AST-Sicherheitsauditor für synthetisierte Skills.

from __future__ import annotations

import ast
from enum import Flag, auto
from typing import List, Set
from pydantic import BaseModel, Field


class ExecutionScope(Flag):
    """
    EN: Bitmask of runtime permissions granted to a procedural System 1 skill.
    DE: Bitmaske der Laufzeitberechtigungen für einen prozeduralen System-1-Skill.
    """
    NONE = 0
    PARSE_DATA = auto()      # Pure structural parsing (HTML, JSON, XML, text)
    HTTP_READ = auto()       # Read-only network requests via supervised client
    STORAGE_WRITE = auto()   # Controlled persistence into target vault
    FILE_SYSTEM = auto()     # Confined local workspace access
    FULL = PARSE_DATA | HTTP_READ | STORAGE_WRITE | FILE_SYSTEM


class SkillCapability(BaseModel):
    """
    EN: Declarative safety and resource manifest enforced prior to skill crystallization.
    DE: Deklaratives Sicherheits- und Ressourcenmanifest, das vor der Skill-Kristallisierung geprüft wird.
    """
    skill_name: str = Field(..., description="Unique procedural skill identifier")
    allowed_scope: ExecutionScope = Field(
        default=ExecutionScope.PARSE_DATA,
        description="Permitted operational scope bitmask"
    )
    allowed_modules: Set[str] = Field(
        default_factory=lambda: {
            "bs4", "re", "json", "typing", "datetime", "urllib", "math", "html"
        },
        description="Strict whitelist of root Python packages allowed in imports"
    )
    required_entrypoint: str = Field(
        default="extract",
        description="Mandatory top-level function name required in the skill module"
    )
    max_execution_time_sec: float = Field(
        default=5.0,
        description="Execution timeout threshold in seconds"
    )

    class Config:
        arbitrary_types_allowed = True


class SecurityViolationError(Exception):
    """
    EN: Raised when synthesized or refactored code violates SkillCapability policies.
    DE: Wird ausgelöst, wenn synthetisierter Code gegen SkillCapability-Richtlinien verstößt.
    """
    pass


class ASTSafetyAuditor:
    """
    EN: Static Abstract Syntax Tree (AST) auditor blocking unauthorized imports,
        dangerous built-in calls, and reflective dunder attribute traversal.
    DE: Statischer AST-Auditor zur Blockierung unzulässiger Importe, gefährlicher
        Built-in-Aufrufe und reflektiver Dunder-Attributzugriffe.
    """

    BANNED_BUILTINS: Set[str] = {
        "eval", "exec", "compile", "__import__", "open", "input",
        "globals", "locals", "vars", "breakpoint", "memoryview"
    }

    BANNED_MODULES: Set[str] = {
        "os", "sys", "subprocess", "socket", "shutil", "pathlib",
        "importlib", "ctypes", "multiprocessing", "threading",
        "http", "requests", "httpx", "urllib3", "aiohttp"
    }

    ALLOWED_DUNDERS: Set[str] = {
        "__init__", "__str__", "__repr__", "__name__", "__doc__", "__len__"
    }

    def __init__(self, capability: SkillCapability) -> None:
        self.capability = capability

    def audit(self, source_code: str) -> List[str]:
        """
        EN: Inspects Python source code via AST and returns a list of security violations.
            An empty list indicates full compliance with the SkillCapability manifest.
        DE: Prüft Python-Quellcode über den AST und gibt eine Liste von Verstößen zurück.
            Eine leere Liste bestätigt die vollständige Konformität mit SkillCapability.
        """
        violations: List[str] = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            return [f"SyntaxError during AST parsing: {exc}"]

        entrypoint_found = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.capability.required_entrypoint:
                entrypoint_found = True

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in self.BANNED_MODULES or root_pkg not in self.capability.allowed_modules:
                        violations.append(
                            f"Prohibited import '{alias.name}': not permitted by capability profile."
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    if root_pkg in self.BANNED_MODULES or root_pkg not in self.capability.allowed_modules:
                        violations.append(
                            f"Prohibited import from '{node.module}': not permitted by capability profile."
                        )

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.BANNED_BUILTINS:
                    violations.append(
                        f"Prohibited dangerous built-in function call: '{node.func.id}()'."
                    )

            elif isinstance(node, ast.Attribute):
                if node.attr.startswith("__") and node.attr.endswith("__"):
                    if node.attr not in self.ALLOWED_DUNDERS:
                        violations.append(
                            f"Prohibited reflective dunder attribute access: '{node.attr}'."
                        )

        if not entrypoint_found:
            violations.append(
                f"Missing mandatory entrypoint function 'def {self.capability.required_entrypoint}(...)'."
            )

        return violations

    def assert_safe(self, source_code: str) -> None:
        """
        EN: Enforces AST safety and raises SecurityViolationError upon any violation.
        DE: Erzwingt AST-Sicherheit und löst bei Verstößen SecurityViolationError aus.
        """
        violations = self.audit(source_code)
        if violations:
            raise SecurityViolationError(
                f"Skill '{self.capability.skill_name}' rejected by ASTSafetyAuditor: "
                + "; ".join(violations)
            )
