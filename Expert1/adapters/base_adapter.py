"""
adapters/base_adapter.py
Expert 1 — TargetAgentAdapter Abstract Interface

Expert 1 通过此接口与被测 Agent 交互，不关心 Agent 的具体类型
（API / Web / File / Mock）。
"""

from abc import ABC, abstractmethod


class TargetAgentAdapter(ABC):
    """
    Expert 1 与被测 Agent 的统一接口。
    所有具体 Adapter（API / Web / Mock）必须继承此类并实现全部方法。
    """

    @abstractmethod
    def send_message(self, message: str) -> str:
        """
        向 Agent 发送一条消息，返回 Agent 的响应文本。

        Args:
            message: 发送给 Agent 的消息字符串

        Returns:
            Agent 的响应文本

        Raises:
            AdapterTimeoutError:  Agent 响应超时
            AdapterUnavailableError: Agent 不可用
        """

    @abstractmethod
    def reset_session(self) -> None:
        """
        重置会话状态，开始新的独立对话。
        每条测试消息后必须调用，防止跨测试上下文污染。
        """

    @abstractmethod
    def get_agent_info(self) -> dict:
        """
        返回 Agent 的基本信息。

        Returns:
            dict with keys: name, type, description, version (optional)
        """

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查 Agent 当前是否可用（连接正常，服务运行中）。
        """


class AdapterTimeoutError(Exception):
    """Agent 响应超时"""


class AdapterUnavailableError(Exception):
    """Agent 服务不可用"""
