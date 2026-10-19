"""LLM 结构化提取与生成的强类型输出模型。"""
from __future__ import annotations

from pydantic import BaseModel


class RecommendationOutput(BaseModel):
    summary: str
    business_advice: str
    disclaimer: str
