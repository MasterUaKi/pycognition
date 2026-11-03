# Version: 0.1.1 | Release Date: 2026-11-03
from enum import Enum
import json
import os
import re
import time
from typing import Any, Dict, List, Optional

import httpx

from pycognition.core.system2 import BaseSystem2
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionResult,
    ExecutionStatus,
    SkillSignature,
    Task,
)


class LLMProvider(str, Enum):
    """Поддерживаемые провайдеры языковых моделей."""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    CUSTOM = "custom"


DEFAULT_BASE_URLS: Dict[LLMProvider, str] = {
    LLMProvider.OPENAI: "https://api.openai.com/v1",
    LLMProvider.DEEPSEEK: "https://api.deepseek.com",
    LLMProvider.CUSTOM: "http://localhost:8000/v1",
}

DEFAULT_MODELS: Dict[LLMProvider, str] = {
    LLMProvider.OPENAI: "gpt-4o",
    LLMProvider.DEEPSEEK: "deepseek-chat",
    LLMProvider.CUSTOM: "default-model",
}


class LLMDeliberator(BaseSystem2):
    """
    Делиберативный контур рассуждений (Система 2).
    Оркестрирует глубокий логический вывод через API OpenAI и DeepSeek,
    а также синтезирует спецификации новых детерминированных навыков.
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.provider = provider
        self.api_key = api_key or self._resolve_api_key(provider)
        self.base_url = (base_url or DEFAULT_BASE_URLS[provider]).rstrip("/")
        self.model = model or DEFAULT_MODELS[provider]
        self.timeout = timeout
        self._external_client = client

    def _resolve_api_key(self, provider: LLMProvider) -> str:
        """Извлекает ключ авторизации из переменных окружения."""
        if provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_API_KEY", "")
        if provider == LLMProvider.DEEPSEEK:
            return os.getenv("DEEPSEEK_API_KEY", "")
        return os.getenv("CUSTOM_LLM_API_KEY", "")

    def _get_client(self) -> httpx.AsyncClient:
        """Возвращает переданный клиент или создает новый экземпляр."""
        if self._external_client is not None:
            return self._external_client
        return httpx.AsyncClient(timeout=self.timeout)

    async def deliberate(self, task: Task) -> ExecutionResult:
        """
        Решает сложную задачу через вызов LLM с замером времени и фиксацией токенов.
        """
        start_time = time.perf_counter()
        endpoint = f"{self.base_url}/chat/completions"

        system_prompt = (
            "Ты — аналитический контур Системы 2 когнитивной архитектуры. "
            "Твоя задача — глубоко проанализировать запрос, спланировать решение "
            "и предоставить логически выверенный, детерминированный ответ."
        )

        user_content = task.prompt
        if task.payload:
            payload_str = json.dumps(task.payload, ensure_ascii=False, indent=2, default=str)
            user_content = f"{task.prompt}\n\nВходные данные:\n{payload_str}"

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        client = self._get_client()
        should_close = self._external_client is None

        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            latency_ms = (time.perf_counter() - start_time) * 1000.0

            if response.status_code != 200:
                return ExecutionResult(
                    task_id=task.id,
                    track_used=CognitiveTrack.SYSTEM_2,
                    status=ExecutionStatus.FAILURE,
                    output=None,
                    latency_ms=latency_ms,
                    error_message=(
                        f"Ошибка API {self.provider.value} (HTTP {response.status_code}): "
                        f"{response.text}"
                    ),
                )

            data = response.json()
            output_text = data["choices"][0]["message"]["content"]
            usage_data = data.get("usage", {})
            token_usage = {
                "prompt_tokens": usage_data.get("prompt_tokens", 0),
                "completion_tokens": usage_data.get("completion_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0),
            }

            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_2,
                status=ExecutionStatus.SUCCESS,
                output=output_text,
                latency_ms=latency_ms,
                token_usage=token_usage,
            )

        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                task_id=task.id,
                track_used=CognitiveTrack.SYSTEM_2,
                status=ExecutionStatus.FAILURE,
                output=None,
                latency_ms=latency_ms,
                error_message=f"Сетевое исключение при вызове {self.provider.value}: {str(exc)}",
            )
        finally:
            if should_close:
                await client.aclose()

    async def synthesize_skill(
        self, task: Task, solution_context: str
    ) -> Optional[SkillSignature]:
        """
        Анализирует контекст решения задачи и синтезирует сигнатуру процедурного навыка.
        """
        endpoint = f"{self.base_url}/chat/completions"

        synthesis_prompt = (
            "На основе задачи и полученного решения сформулируй интерфейс детерминированного "
            "Python-навыка для процедурной памяти (Система 1). "
            "Ответь ИСКЛЮЧИТЕЛЬНО валидным JSON-объектом следующей структуры:\n"
            "{\n"
            '  "name": "имя_функции_в_snake_case",\n'
            '  "description": "краткое назначение функции",\n'
            '  "parameters_schema": {"параметр": "тип_или_описание"},\n'
            '  "return_schema": {"результат": "тип_или_описание"}\n'
            "}"
        )

        messages = [
            {"role": "system", "content": synthesis_prompt},
            {
                "role": "user",
                "content": f"Задача: {task.prompt}\n\nКонтекст решения:\n{solution_context}",
            },
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        client = self._get_client()
        should_close = self._external_client is None

        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            if response.status_code != 200:
                return None

            data = response.json()
            raw_content = data["choices"][0]["message"]["content"].strip()

            json_match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if not json_match:
                return None

            parsed_spec = json.loads(json_match.group(0))

            return SkillSignature(
                name=parsed_spec["name"],
                description=parsed_spec["description"],
                parameters_schema=parsed_spec.get("parameters_schema", {}),
                return_schema=parsed_spec.get("return_schema", {}),
            )

        except Exception:
            return None
        finally:
            if should_close:
                await client.aclose()
