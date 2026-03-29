"""
adapters/api_adapter.py
Expert 1 — APIAdapter Stub

为 Project 3 提供清晰的接口规范。
Project 3 队友需要实现所有 NotImplementedError 的方法。

接口契约（Contract）：
  - send_message(message) 必须返回 Agent 的原始文本响应
  - reset_session() 必须清除所有上下文，使下一条消息是独立的新对话
  - 超时时抛出 AdapterTimeoutError，不能静默返回空字符串
  - is_available() 必须在 Agent 无法响应时返回 False（不能抛异常）

Project 3 实现建议：
  - 如果 Agent 是 REST API：用 requests 库实现 send_message
  - 如果 Agent 是 OpenAI-compatible API：直接调用 /v1/chat/completions
  - session_id 管理：每次 reset_session() 生成新 UUID，在请求头或请求体中传递
"""

import uuid
from .base_adapter import TargetAgentAdapter, AdapterTimeoutError, AdapterUnavailableError


class APIAdapter(TargetAgentAdapter):
    """
    HTTP API 类 Agent 的适配器。

    适用场景：
      - Agent 暴露 REST API 接口（如 POST /chat）
      - Agent 兼容 OpenAI Chat Completions 格式
      - Agent 通过 API Key 做身份认证

    TODO (Project 3):
      实现 send_message / reset_session / get_agent_info / is_available
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: int = 30,
        agent_name: str = "Unknown API Agent",
    ):
        """
        Args:
            base_url:        Agent API 的根 URL，如 "http://localhost:8080"
            api_key:         认证 Key（可选，取决于 Agent 是否需要认证）
            timeout_seconds: 单次请求超时时间，超时后抛 AdapterTimeoutError
            agent_name:      Agent 的显示名称（用于报告）
        """
        self._base_url      = base_url.rstrip("/")
        self._api_key       = api_key
        self._timeout       = timeout_seconds
        self._agent_name    = agent_name
        self._session_id    = str(uuid.uuid4())
        self._message_count = 0

    def send_message(self, message: str) -> str:
        """
        向 Agent 发送一条消息，返回响应文本。

        实现要求：
          - 携带 self._session_id 以维持会话上下文
          - 响应超时（> self._timeout 秒）时抛 AdapterTimeoutError
          - Agent 不可用时抛 AdapterUnavailableError
          - 绝对不能静默返回空字符串

        Expected request format (REST):
            POST {base_url}/chat
            {
                "session_id": "<uuid>",
                "message": "<message>",
                "turn": <message_count>
            }

        Expected response format:
            { "response": "<agent reply text>" }
            or plain text
        """
        raise NotImplementedError(
            "APIAdapter.send_message() not implemented. "
            "Project 3: implement the HTTP request to the target agent here."
        )

    def reset_session(self) -> None:
        """
        重置会话：生成新的 session_id，清除消息计数。
        下一次 send_message() 将开始全新的独立对话。

        实现要求：
          - 生成新的 UUID 作为 session_id
          - 如果 Agent 支持显式的 session 删除 API，调用它
          - 如果 Agent 通过系统消息维持上下文，通知 Agent 清除历史
        """
        self._session_id    = str(uuid.uuid4())
        self._message_count = 0

    def get_agent_info(self) -> dict:
        """
        返回 Agent 的基本信息。

        实现要求：
          - 至少包含 name, type, base_url
          - 如果 Agent 有 /info 或 /metadata 接口，从那里获取
        """
        return {
            "name":     self._agent_name,
            "type":     "api",
            "base_url": self._base_url,
        }

    def is_available(self) -> bool:
        """
        检查 Agent 是否可用（健康检查）。

        实现要求：
          - 发一个 GET /health 或 HEAD / 请求
          - 返回 True 仅当 HTTP 状态码是 2xx
          - 捕获所有网络异常，返回 False（不能抛异常）
          - 超时控制：不超过 5 秒
        """
        raise NotImplementedError(
            "APIAdapter.is_available() not implemented. "
            "Project 3: implement a health check HTTP request here."
        )
