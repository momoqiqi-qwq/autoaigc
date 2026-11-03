# -*- coding: utf-8 -*-
"""单元测试：报告渲染"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reporter import _w, _pad, render_text, render_markdown


class TestWidth(unittest.TestCase):

    def test_chinese_counts_double(self):
        self.assertEqual(_w("字数"), 4)
        self.assertEqual(_w("abc"), 3)
        self.assertEqual(_w("段1"), 3)

    def test_pad_aligns_mixed(self):
        # "字"(2) + 两个空格 = 显示宽度 4
        self.assertEqual(_pad("字", 4), "字  ")
        self.assertEqual(_pad("abcd", 4), "abcd")


def _sample():
    return {
        "engines": ["aigc_zh_v3", "simpleai"],
        "engines_name": {"aigc_zh_v3": "v3", "simpleai": "simple"},
        "role": {"aigc_zh_v3": "classifier", "simpleai": "classifier"},
        "segments": [
            {"index": 1, "len": 100, "probs": {"aigc_zh_v3": 0.95, "simpleai": 0.10},
             "unanimous": False, "suspect": True},
            {"index": 2, "len": 80, "probs": {"aigc_zh_v3": 0.05, "simpleai": 0.02},
             "unanimous": True, "suspect": False},
        ],
        "ai_ratio": {"aigc_zh_v3": 0.55, "simpleai": 0.05},
        "seg_spread": {"aigc_zh_v3": 0.9, "simpleai": 0.08},
        "threshold": 0.56,
        "paragraphs_total": 2,
        "suspect_segments": 1,
        "disagree_segments": 1,
    }


class TestRender(unittest.TestCase):

    def test_text_columns_match_header(self):
        lines = [ln for ln in render_text(_sample(), "样例").splitlines() if ln.strip()]
        header, first_row = lines[1], lines[3]
        self.assertEqual(len(header.split()), len(first_row.split()))
        self.assertIn("⚠歧义", first_row)

    def test_markdown_row_cell_count(self):
        md = render_markdown(_sample(), "样例", "论文.docx")
        rows = [ln for ln in md.splitlines() if ln.startswith("| ") and "---" not in ln]
        counts = {ln.count("|") for ln in rows}
        self.assertEqual(counts, {6})  # 5 列 = 6 个竖线
        self.assertIn("⚠ 歧义", md)


if __name__ == "__main__":
    unittest.main()
