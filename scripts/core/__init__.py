# -*- coding: utf-8 -*-
"""核心模块：CLI 定位、检测调用、交叉分析、报告渲染。"""
from .cli_finder import find_cli
from .detector import run_detect
from .analyzer import cross, verdict
from .reporter import render_text, render_markdown

__all__ = [
    "find_cli",
    "run_detect",
    "cross",
    "verdict",
    "render_text",
    "render_markdown",
]
