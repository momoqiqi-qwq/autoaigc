#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单元测试：交叉分析模块"""
import unittest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import cross, verdict


class TestAnalyzer(unittest.TestCase):
    """测试交叉分析逻辑"""

    def test_cross_basic(self):
        """测试基本交叉分析"""
        results = [
            {
                "_engine": "aigc_zh_v3",
                "engine_name": "AIGC 中文检测 v3",
                "threshold": 0.56,
                "ai_ratio": 0.65,
                "paragraphs": [
                    {"index": 1, "prob": 0.95, "len": 100},
                    {"index": 2, "prob": 0.10, "len": 80},
                ],
                "_cost": 5.2,
            },
            {
                "_engine": "simpleai",
                "engine_name": "SimpleAI",
                "threshold": 0.56,
                "ai_ratio": 0.30,
                "paragraphs": [
                    {"index": 1, "prob": 0.50, "len": 100},
                    {"index": 2, "prob": 0.05, "len": 80},
                ],
                "_cost": 4.8,
            },
        ]

        c = cross(results)

        self.assertEqual(c["paragraphs_total"], 2)
        self.assertEqual(len(c["engines"]), 2)
        self.assertIn("aigc_zh_v3", c["engines"])
        self.assertIn("simpleai", c["engines"])
        self.assertEqual(c["suspect_segments"], 1)  # 只有第一段疑似

    def test_cross_segment_counts_not_match(self):
        """测试切段数不一致"""
        results = [
            {
                "_engine": "aigc_zh_v3",
                "paragraphs": [{"index": 1, "prob": 0.95}],
                "ai_ratio": 0.65,
                "_cost": 5.0,
            },
            {
                "_engine": "simpleai",
                "paragraphs": [
                    {"index": 1, "prob": 0.50},
                    {"index": 2, "prob": 0.10},
                ],
                "ai_ratio": 0.30,
                "_cost": 4.0,
            },
        ]

        with self.assertRaises(RuntimeError) as ctx:
            cross(results)
        self.assertIn("切段数不一致", str(ctx.exception))

    def test_verdict_unanimous_clean(self):
        """测试一致通过的裁决"""
        c = {
            "paragraphs_total": 3,
            "ai_ratio": {"aigc_zh_v3": 0.10, "simpleai": 0.05},
            "role": {"aigc_zh_v3": "classifier", "simpleai": "classifier"},
            "engines": ["aigc_zh_v3", "simpleai"],
            "engines_name": {"aigc_zh_v3": "v3", "simpleai": "simple"},
            "suspect_segments": 0,
            "disagree_segments": 0,
        }

        title, detail = verdict(c)
        self.assertEqual(title, "一致通过")
        self.assertIn("干净", detail)

    def test_verdict_ratio_conflict(self):
        """测试篇级冲突的裁决"""
        c = {
            "paragraphs_total": 3,
            "ai_ratio": {"aigc_zh_v3": 0.80, "simpleai": 0.20},
            "role": {"aigc_zh_v3": "classifier", "simpleai": "classifier"},
            "engines": ["aigc_zh_v3", "simpleai"],
            "engines_name": {"aigc_zh_v3": "v3", "simpleai": "simple"},
            "suspect_segments": 2,
            "disagree_segments": 0,
        }

        title, detail = verdict(c)
        self.assertEqual(title, "两把尺子不一致")
        self.assertIn("80.0%", detail)
        self.assertIn("20.0%", detail)


if __name__ == '__main__':
    unittest.main()
