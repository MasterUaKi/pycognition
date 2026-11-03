# Version: 0.1.2 | Release Date: 2026-11-03
import math
import re
from typing import Dict, List, Optional, Set, Tuple

from pycognition.core.memory import BaseMemory
from pycognition.schemas import ExecutionResult, SkillSignature, Task


class VectorStoreMemory(BaseMemory):
    """
    Гибридная семантическая память pycognition.
    Поддерживает расщепление snake_case, индексацию триггерных промптов
    и семантическое вычисление уверенности для MetaArbiter.
    """

    def __init__(self) -> None:
        self._skills: Dict[str, SkillSignature] = {}
        self._skill_code: Dict[str, str] = {}
        self._skill_tests: Dict[str, str] = {}
        self._trigger_prompts: Dict[str, List[str]] = {}
        self._execution_history: List[Tuple[Task, ExecutionResult]] = []

    def _tokenize(self, text: str) -> List[str]:
        """
        Токенизирует текст, разбивая знаки пунктуации и подчеркивания (_)
        на пробелы для корректного поиска по snake_case идентификаторам.
        """
        clean_text = re.sub(r"[^\w\s]|_", " ", text.lower(), flags=re.UNICODE)
        return [token for token in clean_text.split() if len(token) > 1]

    def _compute_vector(self, tokens: List[str]) -> Dict[str, float]:
        """Формирует нормализованный вектор частот термов (TF)."""
        if not tokens:
            return {}
        counts: Dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1

        norm = math.sqrt(sum(count**2 for count in counts.values()))
        if norm == 0.0:
            return {}
        return {token: count / norm for token, count in counts.items()}

    def _cosine_similarity(self, vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        """Вычисляет косинусное сходство между двумя векторами."""
        if not vec_a or not vec_b:
            return 0.0
        intersection: Set[str] = set(vec_a.keys()) & set(vec_b.keys())
        return sum(vec_a[token] * vec_b[token] for token in intersection)

    async def save_skill_code(
        self,
        signature: SkillSignature,
        code: str,
        tests: str,
        trigger_prompt: Optional[str] = None,
    ) -> None:
        """Сохраняет навык, его код, тесты и привязанный триггерный промпт."""
        self._skills[signature.name] = signature
        self._skill_code[signature.name] = code
        self._skill_tests[signature.name] = tests

        if signature.name not in self._trigger_prompts:
            self._trigger_prompts[signature.name] = []

        if trigger_prompt and trigger_prompt not in self._trigger_prompts[signature.name]:
            self._trigger_prompts[signature.name].append(trigger_prompt)

    async def find_matching_skill(self, task: Task) -> Optional[Tuple[SkillSignature, float]]:
        """
        Выполняет семантическое сопоставление задачи с пулом навыков,
        учитывая имя функции, описание и ранее сохраненные промпты.
        """
        if not self._skills:
            return None

        task_tokens = self._tokenize(task.prompt)
        task_vector = self._compute_vector(task_tokens)

        best_skill: Optional[SkillSignature] = None
        highest_score = 0.0

        for skill_name, skill in self._skills.items():
            prompts_text = " ".join(self._trigger_prompts.get(skill_name, []))
            index_text = f"{skill.name} {skill.description} {prompts_text}"

            skill_tokens = self._tokenize(index_text)
            skill_vector = self._compute_vector(skill_tokens)

            similarity = self._cosine_similarity(task_vector, skill_vector)
            if similarity > highest_score:
                highest_score = similarity
                best_skill = skill

        if best_skill is not None and highest_score > 0.0:
            return best_skill, round(highest_score, 4)

        return None

    async def log_execution(self, task: Task, result: ExecutionResult) -> None:
        self._execution_history.append((task, result))

    @property
    def history_length(self) -> int:
        return len(self._execution_history)
