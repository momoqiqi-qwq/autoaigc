#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测调用模块：执行 aigc.cmd detect 并解析 JSON"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path


def _extract_json(text: str) -> dict:
    """stdout 里可能有零散非 JSON 行（进度条残留），抓第一个 { 到最后一个 }。

    Args:
        text: aigc.cmd 的 stdout 输出

    Returns:
        解析后的 JSON 字典

    Raises:
        ValueError: 无法解析 JSON
    """
    text = text.strip()
    if not text:
        raise ValueError("stdout 为空")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 容错：提取第一个 { 到最后一个 }
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i:
        return json.loads(text[i:j + 1])

    raise ValueError(f"无法从 stdout 解析出 JSON（前 200 字符）：{text[:200]}")


def run_detect(cli: Path, target: Path | str, engine: str,
               extra: list[str] | None = None) -> dict:
    """跑一次 aigc detect --json，返回解析后的结果。

    Args:
        cli: aigc.cmd 路径
        target: 要检测的文件路径或文本
        engine: 引擎名称（如 aigc_zh_v3）
        extra: 额外参数（如 ["--gpu"]）

    Returns:
        解析后的检测结果，增加了 _engine 和 _cost 字段

    Raises:
        RuntimeError: 命令执行失败
    """
    cmd = [str(cli), "detect", "--engine", engine, "--json"]
    if isinstance(target, Path):
        cmd += ["-f", str(target)]
    else:
        cmd += ["-t", target]
    if extra:
        cmd += extra

    t0 = time.time()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cli.parent)
    )
    cost = time.time() - t0

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(
            f"{engine} 退出码 {proc.returncode}: "
            f"{tail[-1] if tail else '无输出'}"
        )

    data = _extract_json(proc.stdout)
    data["_engine"] = engine
    data["_cost"] = round(cost, 1)
    return data
