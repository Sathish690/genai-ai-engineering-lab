import os
import unittest
from unittest.mock import patch

from extractor.config import ConfigurationError, Settings


class SettingsTests(unittest.TestCase):
    def test_reads_environment_settings(self) -> None:
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"}, clear=True):
            settings = Settings.from_environment()
        self.assertEqual(settings.model, "test-model")

    def test_rejects_missing_key_and_blank_model(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_environment()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": " "}, clear=True):
            with self.assertRaises(ConfigurationError):
                Settings.from_environment()
