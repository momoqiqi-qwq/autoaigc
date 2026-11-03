#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单元测试：CLI 查找模块"""
import unittest
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.cli_finder import find_cli


class TestCliFinder(unittest.TestCase):
    """测试 CLI 查找逻辑"""

    def test_explicit_path_exists(self):
        """测试显式指定存在的路径"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cmd', delete=False) as f:
            f.write("echo test")
            temp_path = f.name

        try:
            result = find_cli(temp_path)
            self.assertEqual(result, Path(temp_path))
        finally:
            os.unlink(temp_path)

    def test_explicit_path_not_exists(self):
        """测试显式指定不存在的路径"""
        with self.assertRaises(SystemExit):
            find_cli("/nonexistent/path/aigc.cmd")

    def test_env_variable(self):
        """测试环境变量 AIGC_CLI"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cmd', delete=False) as f:
            f.write("echo test")
            temp_path = f.name

        try:
            os.environ['AIGC_CLI'] = temp_path
            result = find_cli()
            self.assertEqual(result, Path(temp_path))
        finally:
            os.unlink(temp_path)
            del os.environ['AIGC_CLI']

    def test_current_directory_search(self):
        """测试当前目录搜索"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "aigc.cmd"
            test_file.write_text("echo test")

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = find_cli()
                self.assertEqual(result.name, "aigc.cmd")
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
