# Version: 0.2.0 | Release Date: 2026-11-09
import json
from unittest.mock import AsyncMock

import httpx
import pytest

from pycognition.engine.llm_deliberator import LLMDeliberator, LLMProvider
from pycognition.schemas import CognitiveTrack, ExecutionStatus, Task


@pytest.fixture
def sample_task() -> Task:
    return Task(
        prompt="Рассчитай траекторию полета",
        payload={"velocity": 100, "angle": 45},
    )


def test_initialization_defaults() -> None:
    deliberator = LLMDeliberator()
    assert deliberator.provider == LLMProvider.OPENAI
    assert deliberator.model == "gpt-4o"
    assert deliberator.base_url == "https://api.openai.com/v1"
    assert deliberator.timeout == 60.0


def test_initialization_deepseek() -> None:
    deliberator = LLMDeliberator(
        provider=LLMProvider.DEEPSEEK,
        api_key="sk-deepseek-test",
    )
    assert deliberator.provider == LLMProvider.DEEPSEEK
    assert deliberator.base_url == "https://api.deepseek.com"
    assert deliberator.model == "deepseek-chat"


@pytest.mark.asyncio
async def test_deliberate_openai_success(sample_task: Task) -> None:
    mock_response_data = {
        "choices": [{"message": {"content": "Траектория рассчитана: дальность 1020 м."}}],
        "usage": {
            "prompt_tokens": 40,
            "completion_tokens": 15,
            "total_tokens": 55,
        },
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(mock_response_data).encode("utf-8"),
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="test-key",
        client=mock_client,
    )

    result = await deliberator.deliberate(sample_task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.track_used == CognitiveTrack.SYSTEM_2
    assert "1020 м" in str(result.output)
    assert result.latency_ms >= 0.0
    assert result.token_usage is not None
    assert result.token_usage["total_tokens"] == 55

    mock_client.post.assert_awaited_once()
    called_url = mock_client.post.await_args.args[0]
    assert called_url == "https://api.openai.com/v1/chat/completions"


@pytest.mark.asyncio
async def test_deliberate_deepseek_success(sample_task: Task) -> None:
    mock_response_data = {
        "choices": [{"message": {"content": "DeepSeek: решение получено"}}],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(mock_response_data).encode("utf-8"),
        request=httpx.Request("POST", "https://api.deepseek.com/chat/completions"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.DEEPSEEK,
        api_key="test-key-ds",
        client=mock_client,
    )

    result = await deliberator.deliberate(sample_task)

    assert result.status == ExecutionStatus.SUCCESS
    assert result.output == "DeepSeek: решение получено"
    called_url = mock_client.post.await_args.args[0]
    assert called_url == "https://api.deepseek.com/chat/completions"


@pytest.mark.asyncio
async def test_deliberate_api_error_response(sample_task: Task) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=429,
        text="Rate limit exceeded",
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="key",
        client=mock_client,
    )

    result = await deliberator.deliberate(sample_task)

    assert result.status == ExecutionStatus.FAILURE
    assert "429" in str(result.error_message)


@pytest.mark.asyncio
async def test_deliberate_network_exception(sample_task: Task) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.ConnectTimeout("Таймаут соединения")

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="key",
        client=mock_client,
    )

    result = await deliberator.deliberate(sample_task)

    assert result.status == ExecutionStatus.FAILURE
    assert "Таймаут соединения" in str(result.error_message)


@pytest.mark.asyncio
async def test_synthesize_skill_success(sample_task: Task) -> None:
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "name": "calculate_flight",
                        "description": "Расчет дальности полета",
                        "parameters_schema": {"velocity": "float", "angle": "float"},
                        "return_schema": {"distance": "float"},
                    })
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(mock_response_data).encode("utf-8"),
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="test-key",
        client=mock_client,
    )

    sig = await deliberator.synthesize_skill(sample_task, solution_context="1020 м")
    assert sig is not None
    assert sig.name == "calculate_flight"
    assert sig.description == "Расчет дальности полета"


@pytest.mark.asyncio
async def test_synthesize_skill_failure_invalid_json(sample_task: Task) -> None:
    mock_response_data = {
        "choices": [
            {
                "message": {
                    "content": "Невалидный ответ без json-структуры"
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(mock_response_data).encode("utf-8"),
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="test-key",
        client=mock_client,
    )

    sig = await deliberator.synthesize_skill(sample_task, solution_context="ctx")
    assert sig is None