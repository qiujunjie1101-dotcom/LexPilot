"""自定义业务、模型与检索异常体系。"""
from __future__ import annotations


class ContractReviewError(Exception):
    """合同审查业务异常基类。"""


class ContractNotFoundError(ContractReviewError, KeyError):
    """合同不存在；继承 KeyError 以保持既有调用方的异常捕获语义。"""


class LegalReviewNotFoundError(ContractReviewError, KeyError):
    """人工复核单不存在；继承 KeyError 以保持既有调用方的异常捕获语义。"""


class LLMServiceError(ContractReviewError, RuntimeError):
    """大模型调用失败（网络、鉴权、返回非 JSON 等）。"""
