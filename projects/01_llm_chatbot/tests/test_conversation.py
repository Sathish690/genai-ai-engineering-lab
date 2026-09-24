import unittest

from chatbot.conversation import ConversationHistory


class ConversationHistoryTests(unittest.TestCase):
    def test_keeps_only_the_latest_complete_turns(self) -> None:
        history = ConversationHistory(max_turns=2)
        history.add_turn("one", "first")
        history.add_turn("two", "second")
        history.add_turn("three", "third")

        self.assertEqual(
            history.as_api_messages(),
            [
                {"role": "user", "content": "two"},
                {"role": "assistant", "content": "second"},
                {"role": "user", "content": "three"},
                {"role": "assistant", "content": "third"},
            ],
        )

    def test_clear_removes_all_messages(self) -> None:
        history = ConversationHistory(max_turns=1)
        history.add_turn("hello", "hi")
        history.clear()
        self.assertEqual(history.as_api_messages(), [])

    def test_rejects_non_positive_max_turns(self) -> None:
        with self.assertRaises(ValueError):
            ConversationHistory(max_turns=0)
