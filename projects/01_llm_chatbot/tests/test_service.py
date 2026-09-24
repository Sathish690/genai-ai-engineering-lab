import unittest
from unittest.mock import Mock

from chatbot.service import Chatbot


class ChatbotTests(unittest.TestCase):
    def test_reply_adds_turn_to_next_request(self) -> None:
        provider = Mock()
        provider.generate.side_effect = ["First answer", "Second answer"]
        chatbot = Chatbot(provider, "Be helpful.", history_turns=2)

        self.assertEqual(chatbot.reply("First question"), "First answer")
        self.assertEqual(chatbot.reply("Second question"), "Second answer")
        self.assertEqual(
            provider.generate.call_args_list[1].args[0],
            [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
                {"role": "user", "content": "Second question"},
            ],
        )

    def test_blank_message_is_rejected_without_provider_call(self) -> None:
        provider = Mock()
        chatbot = Chatbot(provider, "Be helpful.")

        with self.assertRaises(ValueError):
            chatbot.reply("   ")
        provider.generate.assert_not_called()
