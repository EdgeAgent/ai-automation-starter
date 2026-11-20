from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Self

import pytest
from pydantic import SecretStr

from examples.server.settings import Settings
from examples.server.worker import generate_text


class FakeOpenAIClient:
    def __init__(self, **kwargs: Any) -> None:
        assert kwargs["api_key"] == "test-provider-key"
        assert kwargs["timeout"] == 60.0
        self.responses = SimpleNamespace(create=self.create_response)
        self.last_request: dict[str, str] = {}

    def create_response(self, *, model: str, input: str) -> SimpleNamespace:
        self.last_request = {"model": model, "input": input}
        return SimpleNamespace(output_text="A mocked answer")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


def test_generate_text_uses_injected_client_without_network() -> None:
    config = Settings(
        openai_api_key=SecretStr("test-provider-key"),
        model="test-model",
    )
    fake_clients: list[FakeOpenAIClient] = []

    def client_factory(**kwargs: Any) -> FakeOpenAIClient:
        client = FakeOpenAIClient(**kwargs)
        fake_clients.append(client)
        return client

    output = generate_text("test prompt", config, client_factory=client_factory)

    assert output == "A mocked answer"
    assert fake_clients[0].last_request == {"model": "test-model", "input": "test prompt"}


def test_generate_text_requires_a_provider_key() -> None:
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not configured"):
        config = Settings(_env_file=None, openai_api_key=None)
        generate_text("test prompt", config, client_factory=FakeOpenAIClient)
