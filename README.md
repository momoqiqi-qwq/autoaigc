# autoaigc

本地优先的 AIGC 率工作流 skill —— 先在本机把「这段会被判成 AI 吗」量成一个数字，再决定动不动手，改完必须复检。

原文不出机器、不上传、不烧任何额度；远程引擎只在最后一步做交叉验证。

## 它解决的几个具体问题

| 常见做法 | 问题 | autoaigc 的做法 |
|---|---|---|
| 丢给在线检测器 | 原文上传、额度消耗、结果不可复现 | 本机 `aigc_zh_v3` 模型离线判，逐段出 prob |
| 只看一个引擎 | 同一句话在不同检测器上能差 57 倍 | 多引擎交叉，分歧大就报警而不是硬下结论 |
| 直接改写 | 部分段落会越改越像 AI | 检测 → 定向改写 → 复检，闭环里带收敛判断 |
| 记住「0.5 是阈值」 | 实际默认 0.56，读 `settings.json` | 阈值来自配置，不写死在脑子里 |

## 优先级

按顺序用，别跳。P2 是一切的基准线 —— 没有本地检测的数字，改写就是闭眼改。

| # | 能力 | 命令 | 什么时候用 |
|---|---|---|---|
| **P1** | 检测 → 定向**规则**改写 → 复检 | `aigc.cmd pipeline` | 分数处于 `amendable`（0.56–0.85） |
| **P1.5** | 检测 → 定向 **LLM** 改写 → 复检 | `paper aigc`（Paper-LocalAI） | 分数 ≥ 0.85 / `saturated`，规则改不动 |
| **P2** | 调用本地 AIGC 率检测模型 | `aigc.cmd detect`、`scripts/aigc_cross.py` | 要数字、要逐段明细 |
| P3 | 引擎选型与校准 | `engines` / `probe` / `benchmark` / `models` / `gpu` | 换引擎前、怀疑尺子不准 |
| P4 | 语体守门 | `aigc.cmd audit` | 交付前最后一道 |
| P5 | 与远程引擎交叉 | `aigc-rate-detect` 技能 | 学校/期刊系统前，本地分与远程分打架时 |

## 依赖

这个仓库里是**技能文档 + 交叉验证脚本**，两个本地 AI 在外部：

- **AIGC_Detector** —— 提供 `aigc.cmd` 与 `aigc_zh_v3` 检测器（自带 Python，无需 pip）。仓库内不包含模型权重。
- **Paper-LocalAI**（可选）—— 1.7B 本地改写模型，`llama-server` 跑在 `:11103`，供 P1.5 使用。

脚本按这个顺序找 `aigc.cmd`：`--cli` 参数 → `AIGC_CLI` 环境变量 → 当前目录上溯 → 已知安装位置。

## 快速开始

```bat
:: 环境自检
aigc.cmd doctor --json
aigc.cmd engines --category detect
```

检测一篇论文（推荐走交叉验证脚本）：

```bat
python scripts\aigc_cross.py 论文.docx
python scripts\aigc_cross.py 论文.docx --md 报告.md
python scripts\aigc_cross.py --batch 论文目录 --md 汇总.md
python scripts\aigc_cross.py --self-check
```

0.56–0.85 走规则闭环：

```bat
aigc.cmd pipeline -f 论文.docx --target 0.2 --rounds 3 --out 改后.txt
```

≥ 0.85 走本地 LLM：

```bat
:: 先起 llama-server，再在 Paper-LocalAI 的 harness 里跑
python -m cli_anything.paper aigc 论文.docx --loop 3 --target 0.20 -o 优化版.docx --json
```

## 目录

```
autoaigc/
├── SKILL.md                 技能入口（给 agent 读的导航）
├── docs/
│   ├── workflows/           P1 / P1.5 / P2 / P5 工作流
│   └── advanced/            引擎选型、语体守门、坑点
├── scripts/
│   ├── aigc_cross.py        多引擎交叉验证
│   ├── core/                CLI 定位 / 检测 / 交叉分析 / 报告渲染
│   └── tests/               单元测试（19 个）
├── references/measured.md   全部实测数据
├── CHANGELOG.md
└── VERSION
```

## 安装到 skills 目录

```bat
git clone https://github.com/momoqiqi-qwq/autoaigc.git "%USERPROFILE%\.skills-manager\skills\autoaigc"
```

DeepSeek Harness 通过 `~/.dsh/skills` 加载技能，把这个目录放进去即可。

## 三条不要忘

- **改完一定复检**：规则和 LLM 改写都可能让部分段分数反升。
- **单引擎不可信**：务必交叉验证，分歧大时先怀疑尺子。
- **饱和段有天花板**：prob ≥ 0.99 的段，规则改写最多到 0.98，该换模型就换。

## 版本

当前 `2.0.1` —— 详见 [CHANGELOG.md](CHANGELOG.md)。
