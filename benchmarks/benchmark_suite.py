# Version: 0.1.5 | Release Date: 2026-11-03
"""
Скрипт экспериментального бенчмаркинга для фреймворка pycognition.
Включает предстартовую валидацию API-ключей, подробный вывод ошибок,
безопасную сериализацию дат, фиксацию триггерных промптов в памяти
и автономный режим (--mock).
"""

import argparse
import asyncio
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional

from pycognition.core.system2 import BaseSystem2
from pycognition.engine.llm_deliberator import LLMDeliberator, LLMProvider
from pycognition.engine.meta_arbiter import MetaArbiter
from pycognition.engine.procedural_runner import ProceduralRunner
from pycognition.engine.runtime import CognitiveRuntime
from pycognition.engine.skill_crystallizer import SkillCrystallizer
from pycognition.memory.registry import SkillRegistry
from pycognition.memory.vector_store import VectorStoreMemory
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    ExecutionStatus,
    SkillSignature,
    Task,
)

CSV_FIELDNAMES = [
    "run_index",
    "task_id",
    "prompt",
    "payload",
    "track_used",
    "status",
    "latency_ms",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "crystallization_triggered",
    "crystallization_latency_ms",
    "crystallization_success",
    "error_message",
    "timestamp",
]


class MockDeliberator(BaseSystem2):
    """Автономный эмулятор Системы 2 для локальной верификации."""

    def __init__(self, simulated_latency_ms: float = 350.0) -> None:
        self.simulated_latency_ms = simulated_latency_ms

    async def deliberate(self, task: Task) -> ExecutionResult:
        start_time = time.perf_counter()
        await asyncio.sleep(self.simulated_latency_ms / 1000.0)

        if "signature" in task.payload:
            sig_name = task.payload["signature"].get("name", "")
            artifacts = self._get_mock_artifacts(sig_name)
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_2,
                status=ExecutionStatus.SUCCESS,
                output=json.dumps(artifacts),
                latency_ms=latency_ms,
                token_usage={"prompt_tokens": 120, "completion_tokens": 90, "total_tokens": 210},
            )

        prompt_lower = task.prompt.lower()
        if "hypotenuse" in prompt_lower:
            a = float(task.payload.get("a", 3.0))
            b = float(task.payload.get("b", 4.0))
            output = (a**2 + b**2) ** 0.5
        elif "celsius" in prompt_lower:
            c = float(task.payload.get("celsius", 0.0))
            output = (c * 9.0 / 5.0) + 32.0
        elif "fibonacci" in prompt_lower:
            n = int(task.payload.get("n", 10))
            output = self._fib(n)
        else:
            output = "Mock analysis: Dual-process cognitive trade-offs evaluated."

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return ExecutionResult(
            task_id=task.id,
            track_used=CognitiveTrack.SYSTEM_2,
            status=ExecutionStatus.SUCCESS,
            output=output,
            latency_ms=latency_ms,
            token_usage={"prompt_tokens": 85, "completion_tokens": 35, "total_tokens": 120},
        )

    async def synthesize_skill(
        self, task: Task, solution_context: str
    ) -> Optional[SkillSignature]:
        prompt_lower = task.prompt.lower()
        if "hypotenuse" in prompt_lower:
            return SkillSignature(
                name="calculate_hypotenuse",
                description="calculate hypotenuse right triangle",
                parameters_schema={"a": "float", "b": "float"},
                return_schema={"result": "float"},
            )
        if "celsius" in prompt_lower:
            return SkillSignature(
                name="celsius_to_fahrenheit",
                description="convert temperature from celsius to fahrenheit",
                parameters_schema={"celsius": "float"},
                return_schema={"result": "float"},
            )
        if "fibonacci" in prompt_lower:
            return SkillSignature(
                name="calculate_fibonacci",
                description="calculate nth fibonacci number",
                parameters_schema={"n": "int"},
                return_schema={"result": "int"},
            )
        return None

    def _get_mock_artifacts(self, skill_name: str) -> Dict[str, str]:
        if skill_name == "calculate_hypotenuse":
            return {
                "code": "import math\n\ndef calculate_hypotenuse(a: float, b: float) -> float:\n    return math.sqrt(a**2 + b**2)\n",
                "tests": "from calculate_hypotenuse import calculate_hypotenuse\n\ndef test_hypo():\n    assert calculate_hypotenuse(3.0, 4.0) == 5.0\n",
            }
        if skill_name == "celsius_to_fahrenheit":
            return {
                "code": "def celsius_to_fahrenheit(celsius: float) -> float:\n    return (celsius * 9.0 / 5.0) + 32.0\n",
                "tests": "from celsius_to_fahrenheit import celsius_to_fahrenheit\n\ndef test_c2f():\n    assert celsius_to_fahrenheit(0.0) == 32.0\n",
            }
        return {
            "code": "def calculate_fibonacci(n: int) -> int:\n    if n <= 0: return 0\n    if n == 1: return 1\n    a, b = 0, 1\n    for _ in range(2, n + 1): a, b = b, a + b\n    return b\n",
            "tests": "from calculate_fibonacci import calculate_fibonacci\n\ndef test_fib():\n    assert calculate_fibonacci(10) == 55\n",
        }

    def _fib(self, n: int) -> int:
        if n <= 0:
            return 0
        if n == 1:
            return 1
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


def get_default_benchmark_tasks() -> List[Dict[str, Any]]:
    return [
        {"prompt": "calculate hypotenuse right triangle", "payload": {"a": 3.0, "b": 4.0}},
        {"prompt": "calculate hypotenuse right triangle", "payload": {"a": 5.0, "b": 12.0}},
        {"prompt": "calculate hypotenuse right triangle", "payload": {"a": 8.0, "b": 15.0}},
        {"prompt": "calculate hypotenuse right triangle", "payload": {"a": 7.0, "b": 24.0}},
        {"prompt": "convert temperature from celsius to fahrenheit", "payload": {"celsius": 0.0}},
        {"prompt": "convert temperature from celsius to fahrenheit", "payload": {"celsius": 100.0}},
        {"prompt": "convert temperature from celsius to fahrenheit", "payload": {"celsius": -40.0}},
        {"prompt": "calculate nth fibonacci number", "payload": {"n": 10}},
        {"prompt": "calculate nth fibonacci number", "payload": {"n": 15}},
        {"prompt": "calculate nth fibonacci number", "payload": {"n": 20}},
        {
            "prompt": "Explain the architectural trade-offs between amortized inference and on-demand LLM reasoning",
            "payload": {},
        },
    ]


def _extract_json_payload(raw_text: str) -> Dict[str, Any]:
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    return json.loads(text)


class BenchmarkSuite:
    def __init__(
        self,
        provider: LLMProvider,
        model: Optional[str],
        api_key: Optional[str],
        storage_dir: Path,
        confidence_threshold: float = 0.55,
        use_mock: bool = False,
    ) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.memory = VectorStoreMemory()
        self.runner = ProceduralRunner()
        self.registry = SkillRegistry(storage_dir=self.storage_dir, runner=self.runner)
        self.crystallizer = SkillCrystallizer(storage_dir=self.storage_dir)
        self.arbiter = MetaArbiter(
            memory=self.memory,
            confidence_threshold=confidence_threshold,
        )

        if use_mock:
            self.deliberator: BaseSystem2 = MockDeliberator()
        else:
            self.deliberator = LLMDeliberator(
                provider=provider,
                model=model,
                api_key=api_key,
            )

        self.runtime = CognitiveRuntime(
            arbiter=self.arbiter,
            system1=self.runner,
            system2=self.deliberator,
            memory=self.memory,
            auto_crystallize=False,
        )

    async def execute_task_with_telemetry(
        self, task: Task, run_index: int
    ) -> Dict[str, Any]:
        cryst_triggered = False
        cryst_success = False
        cryst_latency_ms = 0.0

        result: ExecutionResult = await self.runtime.run(task)

        if result.track_used == CognitiveTrack.SYSTEM_2 and result.status == ExecutionStatus.SUCCESS:
            if task.payload:
                cryst_triggered = True
                cryst_start = time.perf_counter()
                print("\n  [Кристаллизация] Запрос сигнатуры...", end=" ", flush=True)

                try:
                    signature = await self.deliberator.synthesize_skill(
                        task=task,
                        solution_context=str(result.output),
                    )

                    if signature is None:
                        print("❌ Сигнатура не распознана.", end=" ", flush=True)
                    else:
                        print(f"'{signature.name}'. Генерация кода...", end=" ", flush=True)

                        code_request_prompt = (
                            f"Напиши детерминированную Python-функцию '{signature.name}' "
                            f"и набор тестов pytest для нее.\n"
                            f"Требования к коду:\n"
                            f"1. Функция принимает аргументы строго из схемы: {signature.parameters_schema}\n"
                            f"2. Запрещены системные модули (os, sys, subprocess) и eval/exec.\n"
                            f"3. В тестах импортируй строго: 'from {signature.name} import {signature.name}'.\n"
                            f"Ответь ИСКЛЮЧИТЕЛЬНО валидным JSON:\n"
                            '{\n  "code": "исходный_код_функции",\n  "tests": "исходный_код_тестов_pytest"\n}'
                        )

                        code_task = Task(
                            prompt=code_request_prompt,
                            payload={"signature": signature.model_dump(mode="json")},
                        )
                        code_res = await self.deliberator.deliberate(code_task)

                        if code_res.status != ExecutionStatus.SUCCESS or not code_res.output:
                            print(f"❌ Ошибка LLM: {code_res.error_message}", end=" ", flush=True)
                        else:
                            parsed = _extract_json_payload(str(code_res.output))
                            py_code = parsed.get("code", "")
                            py_tests = parsed.get("tests", "")

                            print("Песочница...", end=" ", flush=True)
                            cryst_eval = await self.crystallizer.crystallize(
                                signature=signature,
                                code=py_code,
                                tests_code=py_tests,
                            )

                            if not cryst_eval.success:
                                print(f"❌ Сбой: {cryst_eval.error_message}", end=" ", flush=True)
                            elif cryst_eval.skill_path:
                                self.registry.load_skill_from_file(cryst_eval.skill_path)
                                await self.memory.save_skill_code(
                                    signature=signature,
                                    code=py_code,
                                    tests=py_tests,
                                    trigger_prompt=task.prompt,
                                )
                                cryst_success = True
                                print("✅ Сохранен!", end=" ", flush=True)

                except Exception as exc:
                    print(f"❌ Ошибка конвейера: {type(exc).__name__}: {str(exc)}", end=" ", flush=True)
                finally:
                    cryst_latency_ms = (time.perf_counter() - cryst_start) * 1000.0

        token_usage = result.token_usage or {}
        return {
            "run_index": run_index,
            "task_id": task.id,
            "prompt": task.prompt,
            "payload": json.dumps(task.payload, ensure_ascii=False, default=str),
            "track_used": result.track_used.value,
            "status": result.status.value,
            "latency_ms": round(result.latency_ms, 2),
            "prompt_tokens": token_usage.get("prompt_tokens", 0),
            "completion_tokens": token_usage.get("completion_tokens", 0),
            "total_tokens": token_usage.get("total_tokens", 0),
            "crystallization_triggered": cryst_triggered,
            "crystallization_latency_ms": round(cryst_latency_ms, 2),
            "crystallization_success": cryst_success,
            "error_message": result.error_message or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def run_suite(
        self, tasks_data: List[Dict[str, Any]], output_csv: Path
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        file_exists = output_csv.is_file()

        with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()

            for idx, item in enumerate(tasks_data, start=1):
                task = Task(prompt=item["prompt"], payload=item["payload"])
                print(f"[{idx}/{len(tasks_data)}] '{task.prompt}'...", end=" ", flush=True)

                record = await self.execute_task_with_telemetry(task, run_index=idx)
                records.append(record)
                writer.writerow(record)
                f.flush()

                if record["status"] == ExecutionStatus.FAILURE.value:
                    print(f"-> ⚠️ FAILED: {record['error_message']} ({record['latency_ms']:.1f}ms)")
                else:
                    track_str = record["track_used"].upper()
                    lat_str = f"{record['latency_ms']:.1f}ms"
                    tokens_str = f"{record['total_tokens']} tok"
                    print(f"-> {track_str} ({lat_str}, {tokens_str})")

        return records


def print_summary_report(records: List[Dict[str, Any]]) -> None:
    if not records:
        return

    total_runs = len(records)
    s1_records = [r for r in records if r["track_used"] == CognitiveTrack.SYSTEM_1.value]
    s2_records = [
        r for r in records
        if r["track_used"] == CognitiveTrack.SYSTEM_2.value and r["status"] == ExecutionStatus.SUCCESS.value
    ]
    failed_records = [r for r in records if r["status"] == ExecutionStatus.FAILURE.value]

    s1_count = len(s1_records)
    s2_count = len(s2_records)
    failed_count = len(failed_records)

    s1_lat = [r["latency_ms"] for r in s1_records]
    s2_lat = [r["latency_ms"] for r in s2_records]

    s1_avg = sum(s1_lat) / s1_count if s1_count else 0.0
    s2_avg = sum(s2_lat) / s2_count if s2_count else 0.0

    total_tokens = sum(r["total_tokens"] for r in records)
    s2_avg_tok = (sum(r["total_tokens"] for r in s2_records) / s2_count) if s2_count else 0.0
    hypothetical_total = (s1_count + s2_count) * s2_avg_tok
    saved_pct = (
        ((hypothetical_total - total_tokens) / hypothetical_total) * 100.0
        if hypothetical_total > 0
        else 0.0
    )

    cryst_ok = sum(1 for r in records if r["crystallization_success"])

    print("\n" + "=" * 65)
    print("ИТОГОВЫЙ ОТЧЕТ БЕНЧМАРКИНГА (pycognition)")
    print("=" * 65)
    print(f"Всего задач:                       {total_runs}")
    print(f"Вызовов Системы 1 (Скрипты):       {s1_count} ({(s1_count / total_runs) * 100:.1f}%)")
    print(f"Успешных вызовов Системы 2 (LLM):  {s2_count} ({(s2_count / total_runs) * 100:.1f}%)")
    if failed_count > 0:
        print(f"Сбоев исполнения (Failed):         {failed_count} ({(failed_count / total_runs) * 100:.1f}%)")
    print("-" * 65)
    print(f"Средняя задержка Системы 1:        {s1_avg:.2f} ms")
    print(f"Средняя задержка Системы 2:        {s2_avg:.2f} ms")
    if s1_avg > 0 and s2_avg > 0:
        print(f"Ускорение (Speedup):               {s2_avg / s1_avg:.1f}x")
    print("-" * 65)
    print(f"Фактический расход токенов:        {total_tokens}")
    print(f"Экономия токенов:                   {saved_pct:.1f}%")
    print(f"Кристаллизовано навыков (AST+Test): {cryst_ok}")
    print("=" * 65 + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Бенчмарк-сьют для pycognition.")
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "deepseek", "custom"],
        default="deepseek",
        help="Провайдер LLM",
    )
    parser.add_argument("--mock", action="store_true", help="Использовать MockLLM без реальных вызовов API")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--api-key", type=str, default=None)
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results/metrics_deepseek.csv"))
    parser.add_argument("--skills-dir", type=Path, default=Path("benchmarks/results/deepseek_skills"))
    parser.add_argument("--confidence", type=float, default=0.55)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    provider_enum = LLMProvider(args.provider)

    if not args.mock:
        resolved_key = (
            args.api_key
            or os.getenv("DEEPSEEK_API_KEY" if provider_enum == LLMProvider.DEEPSEEK else "OPENAI_API_KEY")
        )
        if not resolved_key:
            print("\n❌ ОШИБКА: API-ключ не обнаружен!")
            print("Задайте переменную окружения: set DEEPSEEK_API_KEY=ваш_ключ")
            print("Или передайте ключ через флаг: --api-key ваш_ключ\n")
            sys.exit(1)

    suite = BenchmarkSuite(
        provider=provider_enum,
        model=args.model,
        api_key=args.api_key,
        storage_dir=args.skills_dir,
        confidence_threshold=args.confidence,
        use_mock=args.mock,
    )

    tasks_pool = get_default_benchmark_tasks()
    mode_str = "MOCK-РЕЖИМ (Offline)" if args.mock else f"ONLINE [{provider_enum.value}]"
    print(f"Запуск бенчмарка pycognition: {mode_str}. Задач: {len(tasks_pool)}")

    records = await suite.run_suite(tasks_pool, output_csv=args.output)
    print_summary_report(records)
    print(f"Метрики записаны в: {args.output.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
