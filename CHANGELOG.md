# Changelog

All notable changes to autoaigc skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.1] - 2026-11-03

### 修复
- **Fixed**: `core/` 下四个模块补 `from __future__ import annotations`，避免 Python 3.9 及以下导入即 SyntaxError
- **Fixed**: `config.py` 移入 `core/`，模块统一相对导入；去掉 `cli_finder.py` / `analyzer.py` 里 try/except 改 `sys.path` 的补丁和重复的 `import sys`
- **Fixed**: `reporter.py` 的 `render_text` 误删 `engs = c["engines"]` 导致的 NameError
- **Fixed**: P1.5 文档补回拆分时丢失的「两个本地 AI 的落点」表
- **Removed**: `FINAL_REPORT.md`、`OPTIMIZATION_COMPLETE.md`、`REFACTOR_SUMMARY.md`、两个 `.backup` 移出技能目录（这些是重构过程记录，不该随技能加载进上下文）
- **Added**: `tests/test_detector.py`、`tests/test_reporter.py`，测试从 8 个增至 19 个，全部通过

## [2.0.0] - 2026-11-03

### 重大重构

#### 文档结构化（阶段 1）
- **Changed**: SKILL.md 从 267 行瘦身到 104 行（-61%）
- **Added**: 创建 8 个模块化子文档
  - `docs/workflows/P1-pipeline.md` - 规则改写闭环
  - `docs/workflows/P1.5-llm-rewrite.md` - 本地 LLM 改写
  - `docs/workflows/P2-detect.md` - 本地检测模型
  - `docs/workflows/P5-remote-cross.md` - 远程引擎交叉
  - `docs/advanced/engines.md` - 引擎选型与校准
  - `docs/advanced/audit.md` - 语体守门
  - `docs/advanced/pitfalls.md` - 坑点汇总
  - `docs/README.md` - 文档导航索引
- **Added**: `SKILL.md.backup` - 原版备份
- **Improved**: 主文档从 267 行拆成导航入口加 8 个子文档，按主题查找不再需要通读全文

#### 代码模块化（阶段 2）
- **Changed**: `aigc_cross.py` 从 437 行重构为 229 行（-48%）
- **Added**: 模块化架构
  - `config.py` - 配置管理（阈值、引擎、路径）
  - `core/cli_finder.py` - CLI 定位模块
  - `core/detector.py` - 检测调用模块
  - `core/analyzer.py` - 交叉分析模块
  - `core/reporter.py` - 输出渲染模块
- **Added**: 单元测试套件
  - `tests/test_cli_finder.py` - CLI 查找测试
  - `tests/test_analyzer.py` - 交叉分析测试
  - 测试覆盖：8 个测试用例全部通过
- **Added**: `aigc_cross.py.backup` - 原版备份
- **Improved**: 代码可维护性、可测试性、可扩展性显著提升

#### 工程化增强（阶段 3）
- **Added**: `CHANGELOG.md` - 版本历史记录
- **Added**: `VERSION` - 版本号管理
- **Added**: `scripts/README.md` - 脚本使用说明
- **Added**: 测试运行脚本

### 向后兼容
- ✅ 所有原有功能完整保留
- ✅ 命令行接口完全一致
- ✅ JSON 输出格式不变
- ✅ 原版文件已备份

## [1.0.0] - 2026-10-28

### Initial Release
- 本地 AIGC 率多引擎交叉验证
- 支持 aigc_zh_v3、simpleai、zh_perplexity 三个引擎
- 单篇检测与批量处理
- 文本/Markdown 报告输出
- 437 行单体实现
