# -*- coding: utf-8 -*-
"""单元测试：检测调用与 JSON 容错解析"""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.detector import _extract_json, run_detect


class TestExtractJson(unittest.TestCase):
    """stdout 里常混进度条残留，解析必须容错。"""

    def test_pure_json(self):
        self.assertEqual(_extract_json('{"a": 1}'), {"a": 1})

    def test_leading_junk(self):
        self.assertEqual(
            _extract_json("进度 50%\n[ok] 完成\n{\"ai_ratio\": 0.2}\n"),
            {"ai_ratio": 0.2},
        )

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            _extract_json("   ")

    def test_no_json_raises(self):
        with self.assertRaises(ValueError):
            _extract_json("只有文字没有括号")


class _FakeProc:
    def __init__(self, code, out, err=""):
        self.returncode = code
        self.stdout = out
        self.stderr = err


class TestRunDetect(unittest.TestCase):

    def test_success_adds_engine_and_cost(self):
        fake = _FakeProc(0, '{"paragraphs": [], "ai_ratio": 0.1}')
        with patch("core.detector.subprocess.run", return_value=fake):
            data = run_detect(Path("aigc.cmd"), "一段话", "aigc_zh_v3")
        self.assertEqual(data["_engine"], "aigc_zh_v3")
        self.assertIn("_cost", data)
        self.assertEqual(data["ai_ratio"], 0.1)

    def test_nonzero_exit_raises_with_stderr_tail(self):
        fake = _FakeProc(1, "", "权重没下齐\n模型文件缺失")
        with patch("core.detector.subprocess.run", return_value=fake):
            with self.assertRaises(RuntimeError) as ctx:
                run_detect(Path("aigc.cmd"), Path("x.docx"), "simpleai")
        self.assertIn("模型文件缺失", str(ctx.exception))

    def test_file_target_uses_dash_f(self):
        fake = _FakeProc(0, "{}")
        with patch("core.detector.subprocess.run", return_value=fake) as run:
            run_detect(Path("aigc.cmd"), Path("论文.docx"), "aigc_zh_v3", ["--gpu"])
        cmd = run.call_args.args[0]
        self.assertIn("-f", cmd)
        self.assertIn("--gpu", cmd)


if __name__ == "__main__":
    unittest.main()
