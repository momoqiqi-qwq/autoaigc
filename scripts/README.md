# autoaigc Scripts

本目录包含 autoaigc 技能包的 Python 脚本和模块。

## 主要脚本

### aigc_cross.py

**多引擎交叉验证主程序**

```bash
# 单篇检测
python aigc_cross.py 论文.docx

# 指定引擎
python aigc_cross.py 论文.docx --engines aigc_zh_v3,simpleai,zh_perplexity

# 输出 Markdown 报告
python aigc_cross.py 论文.docx --md 报告.md

# 批量处理
python aigc_cross.py --batch 论文目录 --md 汇总.md

# 环境自检
python aigc_cross.py --self-check
```

**参数说明**：
- `file` - 要检测的文件（txt/md/docx/pdf）
- `--batch DIR` - 批量处理目录
- `--engines` - 引擎列表（逗号分隔），默认 `aigc_zh_v3,simpleai`
- `--cli` - 指定 aigc.cmd 路径
- `--md OUT.md` - 输出 Markdown 报告
- `--json` - 输出 JSON 格式
- `--strict` - 有分歧时退出码为 2
- `--self-check` - 验证环境

**环境变量**：
- `AIGC_CLI` - aigc.cmd 路径
- `AIGC_GPU` - 设为 `1` 启用 GPU 加速

## 模块结构

### config.py
配置管理模块，包含：
- `DEFAULT_ENGINES` - 默认引擎列表
- `DEFAULT_THRESHOLD` - 默认阈值（0.56）
- `DISAGREE_SEG` - 段级分歧阈值（0.30）
- `DISAGREE_RATIO` - 篇级分歧阈值（0.20）
- `KNOWN_CLI_PATHS` - 已知 CLI 安装位置

### core/

#### cli_finder.py
CLI 定位模块，按以下优先级查找 `aigc.cmd`：
1. 显式参数（`--cli`）
2. 环境变量（`AIGC_CLI`）
3. 当前目录上溯
4. 已知安装位置

#### detector.py
检测调用模块：
- `run_detect()` - 执行 `aigc detect --json`
- `_extract_json()` - 解析 JSON 输出（容错处理）

#### analyzer.py
交叉分析模块：
- `cross()` - 合并多引擎结果
- `verdict()` - 生成结论和建议

#### reporter.py
输出渲染模块：
- `render_text()` - 生成终端表格
- `render_markdown()` - 生成 Markdown 报告

### tests/

单元测试套件：
- `test_cli_finder.py` - CLI 查找逻辑测试
- `test_analyzer.py` - 交叉分析逻辑测试

**运行测试**：
```bash
cd scripts
python -m unittest discover -s tests -v
```

## 开发指南

### 添加新引擎类型

1. 在 `core/analyzer.py` 的 `cross()` 中添加引擎角色判断：
```python
role = {
    e: ("新类型" if "关键词" in e.lower() else "classifier")
    for e in ratios
}
```

2. 在 `verdict()` 中处理新类型的裁决逻辑

### 添加新输出格式

在 `core/reporter.py` 中添加新的渲染函数：
```python
def render_新格式(c: dict, title: str) -> str:
    # 实现新格式的渲染
    pass
```

### 自定义配置

编辑 `config.py` 修改默认值：
```python
DEFAULT_THRESHOLD = 0.60  # 提高阈值
KNOWN_CLI_PATHS = (
    Path("你的/自定义/路径/aigc.cmd"),
)
```

## 版本历史

- **2.0.0** (2026-11-03) - 模块化重构
- **1.0.0** (2026-10-28) - 初始版本

详见 [CHANGELOG.md](../CHANGELOG.md)
