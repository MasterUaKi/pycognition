# Version: 0.1.0 | Release Date: 2026-11-03
"""
Раннер масштабного бенчмарка (100 задач) для пакета pycognition.
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

from benchmarks.workload_generator import generate_complex_100_workload

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


class ExperimentRunner:
    def __init__(
        self,
        provider: LLMProvider,
        model: Optional[str],
        api_key: Optional[str],
        storage_dir: Path,
        confidence_threshold: float = 0.55,
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

    async def execute_task(self, task: Task, run_index: int) -> Dict[str, Any]:
        cryst_triggered = False
        cryst_success = False
        cryst_latency_ms = 0.0

        result: ExecutionResult = await self.runtime.run(task)

        # Кристаллизация только если задача была решена Системой 2 и содержит аргументы
        if result.track_used == CognitiveTrack.SYSTEM_2 and result.status == ExecutionStatus.SUCCESS:
            if task.payload:
                cryst_triggered = True
                cryst_start = time.perf_counter()
                print(" -> [Синтез навыка...", end=" ", flush=True)

                try:
                    signature = await self.deliberator.synthesize_skill(
                        task=task,
                        solution_context=str(result.output),
                    )

                    if signature is not None:
                        code_prompt = (
                            f"Напиши детерминированную Python-функцию '{signature.name}' "
                            f"и набор тестов pytest для нее.\n"
                            f"Требования:\n"
                            f"1. Функция принимает аргументы строго из схемы: {signature.parameters_schema}\n"
                            f"2. Запрещены системные модули (os, sys, subprocess) и eval/exec.\n"
                            f"3. В тестах импортируй строго: 'from {signature.name} import {signature.name}'.\n"
                            f"Ответь ИСКЛЮЧИТЕЛЬНО валидным JSON:\n"
                            '{\n  "code": "исходный_код_функции",\n  "tests": "исходный_код_тестов_pytest"\n}'
                        )

                        code_task = Task(
                            prompt=code_prompt,
                            payload={"signature": signature.model_dump(mode="json")},
                        )
                        code_res = await self.deliberator.deliberate(code_task)

                        if code_res.status == ExecutionStatus.SUCCESS and code_res.output:
                            parsed = _extract_json_payload(str(code_res.output))
                            py_code = parsed.get("code", "")
                            py_tests = parsed.get("tests", "")

                            cryst_eval = await self.crystallizer.crystallize(
                                signature=signature,
                                code=py_code,
                                tests_code=py_tests,
                            )

                            if cryst_eval.success and cryst_eval.skill_path:
                                self.registry.load_skill_from_file(cryst_eval.skill_path)
                                await self.memory.save_skill_code(
                                    signature=signature,
                                    code=py_code,
                                    tests=py_tests,
                                    trigger_prompt=task.prompt,
                                )
                                cryst_success = True
                                print(f"✅ '{signature.name}' сохранен]", end=" ", flush=True)
                            else:
                                print(f"❌ Песочница]", end=" ", flush=True)
                except Exception as exc:
                    print(f"❌ Ошибка: {type(exc).__name__}]", end=" ", flush=True)
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

    async def run(self, workload: List[Dict[str, Any]], output_csv: Path) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        file_exists = output_csv.is_file()

        with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            if not file_exists:
                writer.writeheader()

            total = len(workload)
            for idx, item in enumerate(workload, start=1):
                task = Task(prompt=item["prompt"], payload=item["payload"])
                prompt_short = (task.prompt[:42] + "..") if len(task.prompt) > 44 else task.prompt
                print(f"[{idx:03d}/{total:03d}] '{prompt_short}'", end="", flush=True)

                record = await self.execute_task(task, run_index=idx)
                records.append(record)
                writer.writerow(record)
                f.flush()

                track_label = record["track_used"].upper()
                lat_str = f"{record['latency_ms']:.1f}ms"
                tok_str = f"{record['total_tokens']}tok"
                print(f" -> {track_label} ({lat_str}, {tok_str})")

        return records


def print_final_statistics(records: List[Dict[str, Any]]) -> None:
    total_runs = len(records)
    if total_runs == 0:
        return

    s1_items = [r for r in records if r["track_used"] == "system_1"]
    s2_items = [r for r in records if r["track_used"] == "system_2"]

    s1_count = len(s1_items)
    s2_count = len(s2_items)

    s1_lats = [r["latency_ms"] for r in s1_items]
    s2_lats = [r["latency_ms"] for r in s2_items]

    s1_mean = sum(s1_lats) / s1_count if s1_count else 0.0
    s2_mean = sum(s2_lats) / s2_count if s2_count else 0.0

    total_tokens = sum(r["total_tokens"] for r in records)
    avg_s2_tok = (sum(r["total_tokens"] for r in s2_items) / s2_count) if s2_count else 0.0
    hypothetical_total = total_runs * avg_s2_tok
    saved_pct = (
        ((hypothetical_total - total_tokens) / hypothetical_total) * 100.0
        if hypothetical_total > 0
        else 0.0
    )

    cryst_success = sum(1 for r in records if r["crystallization_success"])

    print("\n" + "=" * 70)
    print("ИТОГОВЫЙ ОТЧЕТ ЭКСПЕРИМЕНТА (N = 100 ЗАДАЧ, pycognition)")
    print("=" * 70)
    print(f"Всего задач выполнено:              {total_runs}")
    print(f"Вызовов Системы 1 (Скрипты):       {s1_count} ({(s1_count / total_runs) * 100:.1f}%)")
    print(f"Вызовов Системы 2 (LLM API):        {s2_count} ({(s2_count / total_runs) * 100:.1f}%)")
    print("-" * 70)
    print(f"Средняя задержка Системы 1:        {s1_mean:.3f} ms")
    print(f"Средняя задержка Системы 2:        {s2_mean:.2f} ms")
    if s1_mean > 0:
        print(f"Ускорение (Speedup factor):        {s2_mean / s1_mean:.1f}x")
    print("-" * 70)
    print(f"Фактически израсходовано токенов:   {total_tokens:,}")
    print(f"Оценка расхода без Системы 1:       {int(hypothetical_total):,}")
    print(f"Экономия токенов (Token savings):  {saved_pct:.1f}%")
    print(f"Успешно кристаллизовано навыков:   {cryst_success}")
    print("=" * 70 + "\n")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Бенчмарк на 100 задач.")
    parser.add_argument("--provider", type=str, choices=["openai", "deepseek"], default="deepseek")
    parser.add_argument("--output", type=Path, default=Path("benchmarks/results/metrics_100_deepseek.csv"))
    parser.add_argument("--skills-dir", type=Path, default=Path("benchmarks/results/deepseek_skills_100"))
    parser.add_argument("--confidence", type=float, default=0.55)
    return parser.parse_args()


async def main() -> None:
    args = parse_arguments()
    provider_enum = LLMProvider(args.provider)

    key_var = "DEEPSEEK_API_KEY" if provider_enum == LLMProvider.DEEPSEEK else "OPENAI_API_KEY"
    api_key = os.getenv(key_var)
    if not api_key:
        print(f"\n❌ ОШИБКА: Переменная окружения {key_var} не установлена!")
        sys.exit(1)

    runner = ExperimentRunner(
        provider=provider_enum,
        model=None,
        api_key=api_key,
        storage_dir=args.skills_dir,
        confidence_threshold=args.confidence,
    )

    workload = generate_complex_100_workload(seed=42)
    print(f"Запуск эксперимента pycognition: 100 сложных гетерогенных задач [{provider_enum.value}].")

    records = await runner.run(workload, output_csv=args.output)
    print_final_statistics(records)
    print(f"Результаты измерений успешно сохранены в: {args.output.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
