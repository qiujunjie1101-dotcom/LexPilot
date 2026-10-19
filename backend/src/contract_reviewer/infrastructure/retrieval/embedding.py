"""文本稠密嵌入模型加载与推理封装（当前为确定性哈希向量，可替换为 BGE 系列模型）。"""
from __future__ import annotations

import hashlib
import math
import re


def tokenize(text: str) -> list[str]:
    ascii_tokens = re.findall(r'[a-z0-9_\-]{2,}', text.lower())
    chinese = ''.join(re.findall(r'[\u4e00-\u9fff]', text))
    return ascii_tokens + [chinese[i:i + 2] for i in range(max(0, len(chinese) - 1))]


def hash_vector(text: str, dims: int = 96) -> list[float]:
    vec = [0.0] * dims
    for token in tokenize(text):
        vec[int.from_bytes(hashlib.sha256(token.encode()).digest()[:2], 'big') % dims] += 1
    norm = math.sqrt(sum(v * v for v in vec)) or 1
    return [v / norm for v in vec]


def embed_text(text: str) -> list[float]:
    return hash_vector(text)
