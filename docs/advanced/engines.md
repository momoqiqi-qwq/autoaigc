# P3 · 引擎选型与校准

## 查看可用模型

```bat
aigc.cmd models                                 :: 哪些齐了、缺哪个、多大
aigc.cmd models --download simpleai             :: 按镜像（默认 hf-mirror）补下
aigc.cmd engines --category detect              :: 查看检测类引擎列表
```

## 引擎选择建议

- 中文论文/申报书以 **`aigc_zh_v3`** 为主尺
- `simpleai` 对学术书面语不敏感（易漏判）
- 交叉验证时至少用两个分类器类引擎（不要只用困惑度类）

## 扰动反演（probe）

验证引擎的量程和判别力：

```bat
aigc.cmd probe -f 论文.docx --engine simpleai
```

**输出解读**：
- `verdict` 说「反应稀疏」= 单段结论不可靠，别拿它当唯一依据
- `per_kind`：看哪类改动对这个引擎有反应（例如"删套话"有效，"改数字"无效）

## 基准测试（benchmark）

```bat
aigc.cmd benchmark --engine aigc_zh_v3 --max 15 --md 基准.md
```

**注意**：内置 15 条是**人工快速自检集**，不代表官方成绩；要真水平用 `--samples 你的.jsonl`（每行 `{"text":...,"label":"ai"|"human","lang":"zh"}`）。

## GPU 支持

```bat
aigc.cmd gpu
```

确认是否有真 CUDA。本机 `torch+cpu`，先确认再决定是否用 `--gpu` 标志。

## 模型下载

```bat
aigc.cmd models --download simpleai
```

会真下 400MB~8GB。

**注意**：`qwen3_*` / `humanize_zh_9b` / `ateeqq_paraphraser` 这些 **`model_warehouse` 类引擎只下载权重、不推理**（`rewrite()` 直接 raise）——这个 CLI 里改写只有规则引擎 `aigc_reduce` 真跑；要真 LLM 改写走 **P1.5**（另一套 harness）。
