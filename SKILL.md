---
name: autoaigc
description: 本地优先的 AIGC 率工作流：用本机已下载的检测模型离线判 AI 率（不联网、不上传原文、不烧额度），再按需定向改写、复检、出报告。内置两个本地 AI —— AIGC_Detector 的 aigc_zh_v3 检测器，和 Paper-LocalAI 里 1.7B 改写大模型（llama-server @11103，闭环命令 paper aigc）。当用户说 autoaigc、本地检测 AIGC 率、离线查 AI 率、不联网测一下、批量体检论文、这篇会被判成 AI 吗、降 AI 率、本地大模型改写、复检改完的段、学校系统会不会查出来时使用。
agent_created: true
---

# autoaigc · AIGC 率自动处理

**本地优先**：检测在本机跑完，原文不出机器，不消耗任何额度。远程引擎只在最后一步做交叉验证。

## 入口

```bat
E:\E-Apps\Work TOOL\论文\AIGC_Detector\aigc.cmd
```

自带 Python，无需 pip。

## 优先级（按调用顺序，别跳）

| # | 能力 | 命令 | 什么时候用 | 详细文档 |
|---|---|---|---|---|
| **P1** | 一键自动闭环：检测 → 定向**规则**改写 → 复检 | `pipeline` | 分数在 `amendable`（0.56–0.85），规则有机会 | [P1-pipeline.md](docs/workflows/P1-pipeline.md) |
| **P1.5** | 一键自动闭环：检测 → 定向 **LLM** 改写 → 复检 | `paper aigc`（另一套 harness） | 分数 ≥0.85 / `saturated`，规则改不动 | [P1.5-llm-rewrite.md](docs/workflows/P1.5-llm-rewrite.md) |
| **P2** | **调用本地 AIGC 率检测模型** | `detect`，交叉用 `scripts/aigc_cross.py` | 要数字、要逐段明细、要判断该不该动手 | [P2-detect.md](docs/workflows/P2-detect.md) |
| P3 | 引擎选型与校准 | `engines` / `probe` / `benchmark` / `models` / `gpu` | 换引擎前、怀疑尺子不准、权重没下齐 | [engines.md](docs/advanced/engines.md) |
| P4 | 语体守门（改完自查） | `audit` | 交付前的最后一道 | [audit.md](docs/advanced/audit.md) |
| P5 | 与远程引擎交叉 | `aigc-rate-detect` 技能 | 学校/期刊系统前，本地分与远程分打架时 | [P5-remote-cross.md](docs/workflows/P5-remote-cross.md) |

**P2 是一切的基准线**：没有本地检测的数字，改写就是闭眼改。

## 快速开始

### 首次使用

```bat
:: 环境自检
aigc.cmd doctor --json
aigc.cmd engines --category detect
```

### 最常用场景

**场景 1：检测一篇论文的 AI 率**

```bat
:: 使用交叉验证脚本（推荐）
set S=%USERPROFILE%\.skills-manager\skills\autoaigc\scripts\aigc_cross.py
python "%S%" 论文.docx
```

**场景 2：AI 率 0.56-0.85，用规则改写**

```bat
aigc.cmd pipeline -f 论文.docx --target 0.2 --rounds 3 --out 改后.txt
```

**场景 3：AI 率 ≥ 0.85，必须用 LLM 改写**

```bat
set P=E:\E-Apps\Work TOOL\论文\Paper-LocalAI
%P%\start-local.cmd
cd /d %P%\agent-harness
python -m cli_anything.paper aigc 论文.docx --loop 3 --target 0.20 -o 优化版.docx --json
```

## 文件结构

```
autoaigc/
├── SKILL.md                        本文（快速导航）
├── docs/
│   ├── workflows/                  工作流详细文档
│   │   ├── P1-pipeline.md         规则改写闭环
│   │   ├── P1.5-llm-rewrite.md    本地 LLM 改写
│   │   ├── P2-detect.md           本地检测模型
│   │   └── P5-remote-cross.md     远程引擎交叉
│   └── advanced/                   高级功能
│       ├── engines.md             引擎选型与校准
│       ├── audit.md               语体守门
│       └── pitfalls.md            坑点汇总
├── scripts/
│   ├── aigc_cross.py              多引擎交叉验证入口
│   ├── core/                      CLI 定位 / 检测 / 交叉分析 / 报告渲染
│   ├── tests/                     单元测试
│   └── README.md                  脚本用法与开发说明
└── references/
    └── measured.md                 全部实测数据
```

## 重要提示

- **改完一定复检**：规则和 LLM 改写都可能让部分段分数反升
- **阈值不是 0.5**：默认 0.56（读 `settings.json`）
- **单引擎不可信**：同句可差 57 倍，务必交叉验证
- **饱和段天花板**：规则改写对 prob ≥ 0.99 的段基本无效，最多降到 0.98

## 完整命令与契约

- CLI 完整文档：`E:\E-Apps\Work TOOL\论文\AIGC_Detector\app\CLI.md`
- 测试记录：`E:\E-Apps\Work TOOL\论文\AIGC_Detector\app\tests\TEST.md`

## 相关技能

- `aigc-rate-detect`（远程检测）
- `aigc-reduce`（改写手法）
- `aigc-down-skill`（去 AI 味写作）
