import os
import unittest
from unittest.mock import patch

from chatbot.config import ConfigurationError, Settings


class SettingsTests(unittest.TestCase):
    def test_reads_valid_environment_settings(self) -> None:
        values = {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "test-model",
            "CHATBOT_SYSTEM_PROMPT": "Test prompt",
            "CHATBOT_HISTORY_TURNS": "4",
        }
        with patch.dict(os.environ, values, clear=True):
            settings = Settings.from_environment()

        self.assertEqual(settings.model, "test-model")
        self.assertEqual(settings.history_turns, 4)

    def test_requires_api_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_environment()
