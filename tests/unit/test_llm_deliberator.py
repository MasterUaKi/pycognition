# Version: 0.1.0 | Release Date: 2026-11-02
import json
from unittest.mock import AsyncMock
import httpx
import pytest

from pycognition.engine.llm_deliberator import (
    DEFAULT_BASE_URLS,
    DEFAULT_MODELS,
    LLMDeliberator,
    LLMProvider,
)
from pycognition.schemas import (
    CognitiveTrack,
    ExecutionStatus,
    Task,
)


@pytest.fixture
def sample_task() -> Task:
    return Task(
        prompt="Рассчитай траекторию полета",
        payload={"velocity": 100, "angle": 45},
    )


def test_initialization_defaults() -> None:
    deliberator = LLMDeliberator(provider=LLMProvider.OPENAI, api_key="sk-openai-test")
    assert deliberator.provider == LLMProvider.OPENAI
    assert deliberator.base_url == DEFAULT_BASE_URLS[LLMProvider.OPENAI]
    assert deliberator.model == DEFAULT_MODELS[LLMProvider.OPENAI]
    assert deliberator.api_key == "sk-openai-test"


def test_initialization_deepseek() -> None:
    deliberator = LLMDeliberator(
        provider=LLMProvider.DEEPSEEK,
        api_key="sk-deepseek-test",
    )
    assert deliberator.provider == LLMProvider.DEEPSEEK
    assert deliberator.base_url == "[https://api.deepseek.com](https://api.deepseek.com)"
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
        request=httpx.Request("POST", "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"),
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
    assert called_url == "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"


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
        request=httpx.Request("POST", "[https://api.deepseek.com/chat/completions](https://api.deepseek.com/chat/completions)"),
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
    assert called_url == "[https://api.deepseek.com/chat/completions](https://api.deepseek.com/chat/completions)"


@pytest.mark.asyncio
async def test_deliberate_api_error_response(sample_task: Task) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=401,
        text="Invalid API Key",
        request=httpx.Request("POST", "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="bad-key",
        client=mock_client,
    )

    result = await deliberator.deliberate(sample_task)

    assert result.status == ExecutionStatus.FAILURE
    assert result.output is None
    assert "HTTP 401" in str(result.error_message)


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
    assert "ConnectTimeout" in str(result.error_message)


@pytest.mark.asyncio
async def test_synthesize_skill_success(sample_task: Task) -> None:
    json_skill_spec = {
        "name": "calculate_trajectory",
        "description": "Расчет дальности полета по скорости и углу",
        "parameters_schema": {"velocity": "float", "angle": "float"},
        "return_schema": {"distance": "float"},
    }
    raw_markdown_reply = f"```json\n{json.dumps(json_skill_spec)}\n```"

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps({"choices": [{"message": {"content": raw_markdown_reply}}]}).encode(
            "utf-8"
        ),
        request=httpx.Request("POST", "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="key",
        client=mock_client,
    )

    signature = await deliberator.synthesize_skill(
        task=sample_task,
        solution_context="Дальность вычисляется по формуле v^2 * sin(2a) / g",
    )

    assert signature is not None
    assert signature.name == "calculate_trajectory"
    assert signature.parameters_schema == {"velocity": "float", "angle": "float"}
    assert signature.return_schema == {"distance": "float"}


@pytest.mark.asyncio
async def test_synthesize_skill_failure_invalid_json(sample_task: Task) -> None:
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = httpx.Response(
        status_code=200,
        content=json.dumps(
            {"choices": [{"message": {"content": "Не могу синтезировать JSON"}}]}
        ).encode("utf-8"),
        request=httpx.Request("POST", "[https://api.openai.com/v1/chat/completions](https://api.openai.com/v1/chat/completions)"),
    )
    mock_client.post.return_value = mock_response

    deliberator = LLMDeliberator(
        provider=LLMProvider.OPENAI,
        api_key="key",
        client=mock_client,
    )

    signature = await deliberator.synthesize_skill(
        task=sample_task,
        solution_context="Неструктурированный ответ",
    )

    assert signature is None
