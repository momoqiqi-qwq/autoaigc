# -*- coding: utf-8 -*-
"""配置：阈值、默认引擎、已知 CLI 路径。"""
from __future__ import annotations

from pathlib import Path

# 默认引擎（分类器类）
DEFAULT_ENGINES = ("aigc_zh_v3", "simpleai")

# 检测结果里没带 threshold 时的后备值（与 aigc.cmd 的 settings.json 默认一致）
DEFAULT_THRESHOLD = 0.56

# 段级：两引擎 prob 差多少算分歧
DISAGREE_SEG = 0.30

# 篇级：两引擎 ai_ratio 差多少算两把尺子不一致
DISAGREE_RATIO = 0.20

# cwd 上溯找不到 aigc.cmd 时的后备位置（技能目录不在仓库下，相对查找会失败）
KNOWN_CLI_PATHS = (
    Path(r"E:\E-Apps\Work TOOL\论文\AIGC_Detector\aigc.cmd"),
    Path.home() / r"AIGC_Detector\aigc.cmd",
)
