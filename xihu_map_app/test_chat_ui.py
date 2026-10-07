"""Exercise both chat entry points without changing saved user data."""
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest


class ChatUITests(unittest.TestCase):
    def test_chat_flows(self):
        app_dir = Path(__file__).resolve().parent
        previous = Path.cwd()
        os.chdir(app_dir)
        try:
            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "在此填入你的 DashScope API 密钥"}):
                app = AppTest.from_file(str(app_dir / "xihu_map_app.py"), default_timeout=30).run()
                self.assertFalse(app.exception)
                app.session_state["current_user"] = "test"
                app.session_state["spots"] = [{"name": "苏堤", "x": 44.0, "y": 28.0,
                                                "description": "", "image_file": ""}]
                app.run()
                self.assertFalse(app.exception)
                with patch("chat_api.requests.post") as post:
                    app.button(key="quick_这里有什么历史？").click().run()
                    post.assert_not_called()
                messages = app.session_state["chat_messages"]["苏堤"]
                self.assertIn("本地文化资料", messages[-1]["content"])
                self.assertIn("1089", messages[-1]["content"])

            response = Mock(status_code=200)
            response.json.return_value = {"choices": [{"message": {"content": "模拟在线回复"}}]}
            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-secret"}), patch("chat_api.requests.post") as post:
                post.return_value.__enter__.return_value = response
                app.text_input(key="chat_input_苏堤").input("苏堤诗词").run()
                app.button(key="send_chat").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["chat_messages"]["苏堤"][-1]["content"], "模拟在线回复")
                self.assertIn("苏堤诗词", post.call_args.kwargs["json"]["messages"][-1]["content"])
                self.assertEqual(post.call_args.args[0], "https://api.deepseek.com/chat/completions")
                self.assertEqual(post.call_args.kwargs["json"]["model"], "deepseek-flash")
                self.assertEqual(post.call_args.kwargs["timeout"], (10, 120))

            with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test-secret"}), patch("chat_api.requests.post") as post:
                response.status_code = 401
                post.return_value.__enter__.return_value = response
                app.button(key="quick_游览建议？").click().run()
                self.assertFalse(app.exception)
                self.assertIn("HTTP 401", app.session_state["chat_messages"]["苏堤"][-1]["content"])
                app.button(key="clear_chat").click().run()
                self.assertEqual(len(app.session_state["chat_messages"]["苏堤"]), 1)
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
