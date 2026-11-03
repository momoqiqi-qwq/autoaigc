# autoaigc 文档导航

本目录包含 autoaigc 技能包的详细文档，按功能模块组织。

## 工作流文档 (workflows/)

按 P1 → P1.5 → P2 → P5 优先级顺序使用：

- **[P1-pipeline.md](workflows/P1-pipeline.md)** - 规则改写闭环（分数 0.56-0.85）
- **[P1.5-llm-rewrite.md](workflows/P1.5-llm-rewrite.md)** - 本地 LLM 改写（分数 ≥ 0.85）
- **[P2-detect.md](workflows/P2-detect.md)** - 本地检测模型（一切的基准线）
- **[P5-remote-cross.md](workflows/P5-remote-cross.md)** - 远程引擎交叉验证

## 高级功能 (advanced/)

- **[engines.md](advanced/engines.md)** - 引擎选型、校准、benchmark
- **[audit.md](advanced/audit.md)** - 语体守门（交付前最后一道）
- **[pitfalls.md](advanced/pitfalls.md)** - 所有已知坑点汇总

## 实测数据 (references/)

- **[measured.md](../references/measured.md)** - 三引擎对比、改写天花板、真论文六轮数据

## 返回主文档

[← 返回 SKILL.md](../SKILL.md)
