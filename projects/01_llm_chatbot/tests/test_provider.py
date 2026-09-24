from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from chatbot.provider import OpenAIProvider, ProviderError


class OpenAIProviderTests(unittest.TestCase):
    def test_sends_messages_to_mocked_responses_api(self) -> None:
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text="Hello!")
        provider = OpenAIProvider("not-a-real-key", "test-model", client=client)

        answer = provider.generate([{"role": "user", "content": "Hi"}], "Be helpful.")

        self.assertEqual(answer, "Hello!")
        client.responses.create.assert_called_once_with(
            model="test-model",
            instructions="Be helpful.",
            input=[{"role": "user", "content": "Hi"}],
        )

    def test_empty_mocked_response_raises_error(self) -> None:
        client = Mock()
        client.responses.create.return_value = SimpleNamespace(output_text=" ")
        provider = OpenAIProvider("not-a-real-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            provider.generate([], "Be helpful.")

    def test_mocked_api_error_is_wrapped(self) -> None:
        client = Mock()
        client.responses.create.side_effect = RuntimeError("network problem")
        provider = OpenAIProvider("not-a-real-key", "test-model", client=client)

        with self.assertRaises(ProviderError):
            provider.generate([], "Be helpful.")
