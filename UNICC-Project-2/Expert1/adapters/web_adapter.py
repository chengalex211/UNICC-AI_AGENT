"""
adapters/web_adapter.py
Expert 1 — WebAdapter Stub (Playwright-based)

为 Project 3 提供清晰的接口规范。
适用于没有 API 接口、只能通过 Web UI 交互的 Agent。

依赖：
    pip install playwright
    playwright install chromium

接口契约（Contract）：
  - send_message() 必须等待 Agent 完整输出（不能截断流式输出）
  - reset_session() 必须清除浏览器上下文，等价于"开新标签页"
  - 页面加载超时或元素找不到时抛 AdapterUnavailableError
  - is_available() 检查 URL 是否可访问，不能抛异常

Project 3 实现建议：
  - 用 Playwright async API + asyncio（或同步 API）
  - 输入框定位：建议先用 ID，再 CSS selector，最后 XPath
  - 等待 Agent 响应：用 page.wait_for_selector() 而不是 time.sleep()
  - 流式输出检测：等待一段时间内没有新内容出现再读取
"""

import time
from .base_adapter import TargetAgentAdapter, AdapterTimeoutError, AdapterUnavailableError


class WebAdapter(TargetAgentAdapter):
    """
    Web UI 类 Agent 的适配器（基于 Playwright）。

    适用场景：
      - Agent 只有 Web 聊天界面，没有 API
      - Agent 是 Streamlit / Gradio 应用
      - Agent 需要登录认证

    TODO (Project 3):
      1. 在 __init__ 中初始化 Playwright browser + page
      2. 实现 send_message：定位输入框 → 输入 → 等待响应 → 提取文本
      3. 实现 reset_session：刷新页面或创建新 page
      4. 实现 is_available：检查页面是否加载成功
    """

    def __init__(
        self,
        url: str,
        input_selector: str = "textarea",
        response_selector: str = ".response, .bot-message, [data-testid='bot-message']",
        timeout_seconds: int = 30,
        agent_name: str = "Unknown Web Agent",
        headless: bool = True,
    ):
        """
        Args:
            url:               Agent 的 Web UI 地址，如 "http://localhost:8501"
            input_selector:    聊天输入框的 CSS 选择器
            response_selector: Agent 响应消息的 CSS 选择器
            timeout_seconds:   等待响应的超时时间
            agent_name:        Agent 显示名称（用于报告）
            headless:          是否无头模式（True=后台运行，False=可视化调试）

        Playwright 初始化示例 (Project 3 实现时取消注释):
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=headless)
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            self._page.goto(url)
        """
        self._url               = url
        self._input_selector    = input_selector
        self._response_selector = response_selector
        self._timeout           = timeout_seconds * 1000  # Playwright 用毫秒
        self._agent_name        = agent_name
        self._headless          = headless
        # self._playwright = None
        # self._browser    = None
        # self._page       = None

    def send_message(self, message: str) -> str:
        """
        在 Web UI 中输入消息，等待并返回 Agent 响应文本。

        实现要求：
          1. 定位输入框：self._page.locator(self._input_selector)
          2. 清空并输入消息：locator.fill(message)
          3. 触发发送：locator.press("Enter") 或点击发送按钮
          4. 等待新响应出现：wait_for_selector(self._response_selector, state="visible")
          5. 等待响应完成（流式输出停止）
          6. 提取最后一条响应的文本内容

        流式输出等待示例：
            last_text = ""
            while True:
                current_text = page.locator(response_selector).last.text_content()
                if current_text == last_text:
                    break
                last_text = current_text
                time.sleep(0.5)
        """
        raise NotImplementedError(
            "WebAdapter.send_message() not implemented. "
            "Project 3: implement Playwright interaction here."
        )

    def reset_session(self) -> None:
        """
        重置会话：刷新页面或创建新的 browser context。

        实现要求（选其一，取决于 Agent 实现）：
          Option A（刷新页面）：self._page.reload()
          Option B（新 context）：
            self._context.close()
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            self._page.goto(self._url)
          Option C（点击"New Chat"按钮）：
            self._page.locator("[data-testid='new-chat']").click()
        """
        raise NotImplementedError(
            "WebAdapter.reset_session() not implemented. "
            "Project 3: implement page refresh or new context here."
        )

    def get_agent_info(self) -> dict:
        return {
            "name": self._agent_name,
            "type": "web",
            "url":  self._url,
        }

    def is_available(self) -> bool:
        """
        检查 Web UI 是否可访问。

        实现要求：
          - 尝试 self._page.goto(self._url, timeout=5000)
          - 检查页面 title 或关键元素是否存在
          - 捕获所有异常，返回 False（不能抛异常）
        """
        raise NotImplementedError(
            "WebAdapter.is_available() not implemented. "
            "Project 3: implement a page load check here."
        )

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        在评估完成后调用。

        实现：
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        """
        raise NotImplementedError(
            "WebAdapter.close() not implemented. "
            "Project 3: implement browser cleanup here."
        )
