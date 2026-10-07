import unittest
from unittest.mock import Mock, patch

import requests
from chat_api import ChatError, completion_url, request_chat, valid_api_key


class ChatTests(unittest.TestCase):
    def call(self, response=None, error=None):
        with patch("chat_api.requests.post", side_effect=error) as post:
            if response is not None:
                post.return_value.__enter__.return_value = response
            result = request_chat("sk-test-secret", "https://example.com/v1/", "test", "120", [])
            self.assertEqual(post.call_args.kwargs["timeout"], (10, 120))
            self.assertEqual(post.call_args.args[0], "https://example.com/v1/chat/completions")
            return result

    def test_placeholders(self):
        for value in ("", "在此填入你的 DashScope API 密钥", "DashScope API", "your_api_key", "sk-xxx", "sk-中文", "sk-foo bar", "sk-sp-test-key"):
            self.assertFalse(valid_api_key(value), value)
        self.assertTrue(valid_api_key("sk-test-secret"))
        with patch("chat_api.requests.post") as post:
            with self.assertRaises(ChatError):
                request_chat("DashScope API", "", "test", "120", [])
            post.assert_not_called()

    def test_deepseek_defaults(self):
        from chat_api import DEFAULT_BASE_URL, DEFAULT_MODEL
        self.assertEqual(completion_url(DEFAULT_BASE_URL), "https://api.deepseek.com/chat/completions")
        self.assertEqual(DEFAULT_MODEL, "deepseek-flash")

    def test_endpoints(self):
        for base in ("https://example.com/v1", "https://example.com/v1/", "https://example.com/v1/chat/completions/"):
            self.assertEqual(completion_url(base), "https://example.com/v1/chat/completions")
        for base in ("http://example.com", "https://", "https://example.com:bad", "https://user:pass@example.com", "https://example.com?key=secret"):
            with self.assertRaises(ChatError):
                completion_url(base)

    def test_success(self):
        response = Mock(status_code=200)
        response.json.return_value = {"choices": [{"message": {"content": "西湖回复"}}]}
        self.assertEqual(self.call(response), "西湖回复")

    def test_http_failures(self):
        for code in (401, 402, 403, 404, 429, 500):
            with self.assertRaisesRegex(ChatError, str(code)):
                self.call(Mock(status_code=code))

    def test_invalid_responses(self):
        for body in ({}, {"choices": []}, {"choices": [{"message": {"content": " "}}]}, {"choices": [{"message": {"content": []}}]}):
            response = Mock(status_code=200)
            response.json.return_value = body
            with self.assertRaisesRegex(ChatError, "无效或空"):
                self.call(response)
        response.json.side_effect = ValueError("secret response")
        with self.assertRaisesRegex(ChatError, "无效或空"):
            self.call(response)

    def test_network_failures(self):
        for error in (requests.Timeout("secret"), requests.ConnectionError("secret")):
            with self.assertRaises(ChatError) as caught:
                self.call(error=error)
            self.assertNotIn("secret", str(caught.exception))

    def test_invalid_timeout(self):
        for value in ("0", "-1", "nan", "inf", "invalid"):
            with patch("chat_api.requests.post") as post:
                with self.assertRaises(ChatError):
                    request_chat("sk-test-secret", "", "test", value, [])
                post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
