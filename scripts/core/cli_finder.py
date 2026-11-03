# -*- coding: utf-8 -*-
"""CLI 定位：按 参数 > 环境变量 > 当前目录上溯 > 已知安装位置 找 aigc.cmd。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from .config import KNOWN_CLI_PATHS


def find_cli(explicit: str | None = None) -> Path:
    """返回 aigc.cmd 路径；找不到时 SystemExit。"""
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file():
            return p
        raise SystemExit(f"[x] --cli 指向的文件不存在: {p}")

    env = os.environ.get("AIGC_CLI")
    if env and Path(env).is_file():
        return Path(env)

    here = Path(__file__).resolve()
    for base in [Path.cwd(), *Path.cwd().parents, *here.parents]:
        for name in ("aigc.cmd", "aigc.py", "aigc"):
            cand = base / name
            if cand.is_file():
                return cand

    for cand in KNOWN_CLI_PATHS:
        if cand.is_file():
            print(f"[note] 用已知安装位置: {cand}", file=sys.stderr)
            return cand

    raise SystemExit(
        "[x] 找不到 aigc.cmd。用 --cli 指定，或设环境变量 AIGC_CLI，\n"
        "    例：--cli \"E:\\E-Apps\\Work TOOL\\论文\\AIGC_Detector\\aigc.cmd\""
    )
