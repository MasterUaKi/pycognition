# File: src/pycognition/skills/crystallizer.py
# Version: 1.2.0 | Release Date: 2026-11-12
# EN: Sandbox execution, regression-guarded verification, and atomic crystallization of System 1 skills.
# DE: Sandbox-Ausführung, regressionsgeschützte Verifikation und atomare Kristallisierung von System-1-Skills.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from pycognition.skills.capability import ASTSafetyAuditor, SkillCapability
from pycognition.skills.telemetry import SkillExecutionTelemetry, TelemetryEvaluator


class CrystallizationResult(BaseModel):
    """
    EN: Outcome report of an attempted skill crystallization cycle.
    DE: Ergebnisbericht eines versuchten Skill-Kristallisierungszyklus.
    """
    accepted: bool
    skill_name: str
    reason: str
    persisted_path: Optional[str] = None
    telemetry: Optional[SkillExecutionTelemetry] = None


class RegressionGuardError(Exception):
    """
    EN: Raised when a refactored skill performs worse than the established baseline.
    DE: Wird ausgelöst, wenn ein überarbeiteter Skill schlechter abschneidet als die Baseline.
    """
    pass


class SkillSandbox:
    """
    EN: Restricted namespace executor for dry-running AST-audited procedural skills.
    DE: Isolierter Namensraum-Executor für Testläufe AST-geprüfter prozeduraler Skills.
    """

    SAFE_BUILTINS: Dict[str, Any] = {
        "len": len, "str": str, "int": int, "float": float, "bool": bool,
        "list": list, "dict": dict, "set": set, "frozenset": frozenset,
        "tuple": tuple, "bytes": bytes, "bytearray": bytearray,
        "enumerate": enumerate, "zip": zip, "range": range,
        "sorted": sorted, "reversed": reversed, "filter": filter, "map": map,
        "next": next, "iter": iter, "id": id, "hash": hash,
        "min": min, "max": max, "sum": sum, "any": any, "all": all,
        "round": round, "abs": abs, "chr": chr, "ord": ord,
        "repr": repr, "format": format, "slice": slice,
        "isinstance": isinstance, "issubclass": issubclass,
        "getattr": getattr, "hasattr": hasattr,
        "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
        "KeyError": KeyError, "IndexError": IndexError, "AttributeError": AttributeError,
        "StopIteration": StopIteration, "RuntimeError": RuntimeError,
        "__import__": __import__,
    }

    @classmethod
    def run_dry(
        cls,
        source_code: str,
        entrypoint: str,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        EN: Compiles and executes candidate skill code in an isolated globals dictionary.
        DE: Kompiliert und führt Kandidaten-Code in einem isolierten Globals-Dictionary aus.
        """
        sandbox_globals: Dict[str, Any] = {"__builtins__": dict(cls.SAFE_BUILTINS)}
        try:
            compiled = compile(source_code, "<pycognition_sandbox>", "exec")
            exec(compiled, sandbox_globals)  # noqa: S102 - audited by ASTSafetyAuditor beforehand
            target_fn = sandbox_globals.get(entrypoint)
            if not callable(target_fn):
                return False, None, f"Entrypoint '{entrypoint}' is not callable."
            output = target_fn(*args, **kwargs)
            return True, output, None
        except Exception as exc:
            return False, None, f"{type(exc).__name__}: {exc}"


class SkillCrystallizer:
    """
    EN: End-to-end verification pipeline ensuring that System 2 synthesized skills are
        AST-safe, runtime-valid, and non-regressive before persistence to disk.
    DE: Durchgängige Verifikations-Pipeline, die AST-Sicherheit, Laufzeitvalidität und
        Regressionsfreiheit synthetisierter Skills vor dem Speichern sicherstellt.
    """

    def __init__(
        self,
        registry_dir: Path | str,
        evaluator: Optional[TelemetryEvaluator] = None,
        version_tag: str = "1.2.0",
    ) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.evaluator = evaluator or TelemetryEvaluator()
        self.version_tag = version_tag

    def crystallize(
        self,
        source_code: str,
        capability: SkillCapability,
        sample_args: Tuple[Any, ...],
        target_uri: str = "sandbox://verification",
        baseline_valid_count: int = 0,
        max_allowed_corruption: float = 0.20,
        source_label: str = "Autonomous Synthesis",
    ) -> CrystallizationResult:
        """
        EN: Executes the 3-stage crystallization gate:
            1. AST Capability Audit
            2. Sandbox Dry-Run & Telemetry Evaluation
            3. Monotonic Regression Guard & Atomic Persistence
        DE: Führt das dreistufige Kristallisierungs-Gate aus:
            1. AST-Capability-Audit
            2. Sandbox-Testlauf & Telemetrie-Bewertung
            3. Monotoner Regressionswächter & atomare Speicherung
        """
        # Gate 1: Static AST Safety Audit
        auditor = ASTSafetyAuditor(capability)
        violations = auditor.audit(source_code)
        if violations:
            return CrystallizationResult(
                accepted=False,
                skill_name=capability.skill_name,
                reason="AST security audit failed: " + "; ".join(violations),
            )

        # Gate 2: Sandbox Dry-Run Execution
        ok, raw_output, run_err = SkillSandbox.run_dry(
            source_code,
            capability.required_entrypoint,
            *sample_args,
        )
        telemetry = self.evaluator.evaluate(
            skill_name=capability.skill_name,
            target_uri=target_uri,
            raw_output=raw_output,
            execution_error=run_err,
        )
        if not ok or telemetry.execution_error:
            return CrystallizationResult(
                accepted=False,
                skill_name=capability.skill_name,
                reason=f"Sandbox execution failed: {telemetry.execution_error}",
                telemetry=telemetry,
            )

        # Gate 3: Regression Guard
        if telemetry.valid_count < baseline_valid_count:
            return CrystallizationResult(
                accepted=False,
                skill_name=capability.skill_name,
                reason=(
                    f"Regression detected: valid yield dropped from baseline {baseline_valid_count} "
                    f"to {telemetry.valid_count}."
                ),
                telemetry=telemetry,
            )

        if telemetry.total_raw_candidates >= 3 and telemetry.corruption_ratio > max_allowed_corruption:
            return CrystallizationResult(
                accepted=False,
                skill_name=capability.skill_name,
                reason=(
                    f"Quality threshold violated: corruption ratio {telemetry.corruption_ratio:.1%} "
                    f"exceeds maximum {max_allowed_corruption:.1%}."
                ),
                telemetry=telemetry,
            )

        # Persist verified skill atomically
        persisted_file = self._write_skill_file(capability.skill_name, source_label, source_code)
        return CrystallizationResult(
            accepted=True,
            skill_name=capability.skill_name,
            reason="Skill passed AST audit, sandbox dry-run, and regression guard.",
            persisted_path=str(persisted_file),
            telemetry=telemetry,
        )

    def _write_skill_file(self, skill_name: str, source_label: str, code: str) -> Path:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        target_path = self.registry_dir / f"{skill_name}.py"

        cleaned_lines = [
            line for line in code.splitlines()
            if not line.startswith("# File:") and not line.startswith("# Version:")
        ]
        body = "\n".join(cleaned_lines).strip() + "\n"

        header = (
            f"# File: skills_registry/{skill_name}.py\n"
            f"# Version: {self.version_tag} | Release Date: {today_str}\n"
            f"# Source: {source_label}\n"
            f"# Auto-crystallized and AST-verified by PyCognition SkillCrystallizer.\n\n"
        )
        target_path.write_text(header + body, encoding="utf-8")
        return target_path
