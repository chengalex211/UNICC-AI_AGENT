# -*- coding: utf-8 -*-
"""
Expert 1 主动攻击 HTTP 接口

运行方式（在 Capstone 项目根目录）:
  pip install -r api/requirements.txt
  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

接口:
  POST /evaluate/expert1-attack
  Body: agent_id, system_name, system_description, 以及可选的 purpose, deployment_context, data_access, risk_indicators, mock_level
  Response: Expert 1 完整报告（含 PROBE / BOUNDARY / ATTACK 与打分）
"""

import os
import sys

_CAPSTONE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXPERT1_DIR = os.path.join(_CAPSTONE_DIR, "Expert1")

from dataclasses import asdict, is_dataclass
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


def _ensure_serializable(obj: Any) -> Any:
    """递归把 dataclass / 嵌套结构转为可 JSON 序列化的 dict/list。"""
    if is_dataclass(obj) and not isinstance(obj, type):
        return _ensure_serializable(asdict(obj))
    if isinstance(obj, dict):
        return {k: _ensure_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_ensure_serializable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)

app = FastAPI(
    title="UNICC Expert 1 Attack API",
    description="Expert 1 安全与对抗测试（含主动攻击 Phase 3）HTTP 接口",
    version="1.0.0",
)


# ─── 请求体 ───────────────────────────────────────────────────────────────────

class Expert1AttackRequest(BaseModel):
    """发起 Expert 1 完整评估的请求体，与 AgentSubmission / AgentProfile 对齐。"""
    agent_id: str = Field(..., description="唯一标识，如 refugee-assist-v2")
    system_name: str = Field("", description="系统展示名称")
    system_description: str = Field(..., description="系统描述，供 Expert 1 分析")
    purpose: str = Field("", description="用途说明，可选")
    deployment_context: str = Field("", description="部署场景")
    data_access: list[str] = Field(default_factory=list, description="涉及的数据访问类型")
    risk_indicators: list[str] = Field(default_factory=list, description="风险关键词")
    mode: str = Field("B", description="Mode A=文档分析（仅打分，无 live 攻击） | Mode B=完整主动攻击（PROBE→BOUNDARY→ATTACK）")
    mock_level: str = Field("medium", description="Mode B 时 MockAdapter 安全等级: low | medium | high")
    backend: str = Field("claude", description="LLM 后端: claude | mock")


# ─── 调用 Expert 1 并返回报告 ─────────────────────────────────────────────────

def run_expert1_attack(req: Expert1AttackRequest) -> dict:
    # 仅在调用时把 Expert1 加入 path，避免污染标准库 imports（如 types）
    if _EXPERT1_DIR not in sys.path:
        sys.path.insert(0, _EXPERT1_DIR)
    from expert1_module import run_full_evaluation
    from expert1_router import AgentProfile, ClaudeBackend, MockLLMBackend
    from adapters.mock_adapter import MockAdapter

    profile = AgentProfile(
        agent_id=req.agent_id,
        name=req.system_name or req.agent_id,
        description=req.system_description,
        purpose=req.purpose or "",
        deployment_context=req.deployment_context or "",
        data_access=req.data_access or [],
        risk_indicators=req.risk_indicators or [],
    )
    # Mode A: 文档分析（adapter=None，无 live 攻击）；Mode B: 完整主动攻击（MockAdapter）
    adapter = None if (req.mode or "B").upper() == "A" else MockAdapter(security_level=req.mock_level)

    if req.backend == "mock":
        llm = MockLLMBackend()
    else:
        try:
            llm = ClaudeBackend()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Claude 后端不可用（需 ANTHROPIC_API_KEY）: {e}. 可改用 backend='mock' 做联调。"
            )

    try:
        report = run_full_evaluation(profile, adapter=adapter, llm=llm)
        return _ensure_serializable(report.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/expert1-attack", summary="发起 Expert 1 主动攻击评估")
def expert1_attack(request: Expert1AttackRequest):
    """
    对给定系统描述执行 Expert 1 完整流程（PROBE → BOUNDARY → ATTACK），
    使用 MockAdapter 模拟被测 Agent，返回完整报告（含攻击轮次、技术、打分等）。
    """
    return run_expert1_attack(request)


@app.get("/health")
def health():
    return {"status": "ok", "service": "expert1-attack-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
