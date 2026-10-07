"""DeepSeek chat transport; independent of the Streamlit UI."""
import math
from urllib.parse import urlsplit

import requests

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"


class ChatError(Exception):
    """Safe, user-facing failure description."""


def clean_value(value):
    return (value or "").strip().strip('\"\'').strip()


def valid_api_key(value):
    value = clean_value(value)
    markers = ("填入", "替换", "密钥", "your", "placeholder", "dashscope", "api_key", "api key", "xxx", "<", ">")
    return bool(value and value.isascii() and not value.startswith("sk-sp-") and not any(c.isspace() for c in value)
                and not any(marker in value.lower() for marker in markers))


def completion_url(base_url):
    value = clean_value(base_url).rstrip("/") or DEFAULT_BASE_URL
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise ChatError("API 地址配置无效，请检查 DEEPSEEK_BASE_URL。") from None
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment or not value.isascii()):
        raise ChatError("API 地址必须是有效的 HTTPS 地址，且不包含账号、查询参数或片段。")
    return value if parsed.path.endswith("/chat/completions") else value + "/chat/completions"


def read_timeout(value):
    try:
        seconds = float(value)
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError
        return seconds
    except (TypeError, ValueError):
        raise ChatError("DEEPSEEK_TIMEOUT 必须是大于 0 的秒数。") from None


def request_chat(api_key, base_url, model, timeout, messages):
    if not valid_api_key(api_key):
        raise ChatError("尚未配置有效的 DeepSeek API Key。")
    url = completion_url(base_url)
    seconds = read_timeout(timeout)
    try:
        with requests.post(url, headers={"Authorization": "Bearer " + clean_value(api_key)},
                           json={"model": model, "messages": messages,
                                 "temperature": 0.7, "max_tokens": 2000,
                                 "thinking": {"type": "disabled"}},
                           timeout=(10, seconds)) as response:
            if response.status_code != 200:
                hints = {401: "DeepSeek 密钥无效", 402: "DeepSeek 账户余额不足", 403: "没有模型或服务访问权限",
                         404: "请检查 endpoint 和模型名称", 429: "请求限流或额度不足"}
                hint = hints.get(response.status_code, "服务暂时不可用，请稍后重试")
                raise ChatError(f"AI 服务返回 HTTP {response.status_code}：{hint}。")
            try:
                body = response.json()
                content = body["choices"][0]["message"]["content"]
                if not isinstance(content, str) or not content.strip():
                    raise ValueError
                return content.strip()
            except (ValueError, KeyError, IndexError, TypeError):
                raise ChatError("AI 服务返回了无效或空的回复，请稍后重试。") from None
    except requests.exceptions.Timeout:
        raise ChatError(f"AI 请求超时（连接 10 秒，读取 {seconds:g} 秒），请稍后重试。") from None
    except requests.exceptions.RequestException:
        raise ChatError("无法连接 AI 服务，请检查网络和 API 地址。") from None
