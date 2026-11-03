# P2 · 调用本地 AIGC 率检测模型

**P2 是一切的基准线**：没有本地检测的数字，改写就是闭眼改。

## 入口

```bat
E:\E-Apps\Work TOOL\论文\AIGC_Detector\aigc.cmd
```

自带 Python，无需 pip。

## 环境自检（第一次必跑）

```bat
aigc.cmd doctor --json
aigc.cmd engines --category detect
```

只认标了「已下载」的引擎；未下载的会在第一次推理时报错，先用 `aigc.cmd models` 看清。

## 单篇检测

```bat
aigc.cmd detect -f 论文.docx
aigc.cmd detect -f 论文.docx --report 报告.html
aigc.cmd detect -f 论文.docx --engine aigc_zh_v3 --json
aigc.cmd detect -t "要测的一段话" --engine simpleai --json
type 片段.txt | aigc.cmd detect --json
```

**支持格式**：txt / md / docx / pdf（PDF 已做页眉页脚剔除与双栏重排）

**分段规则**：按空行分段，短于 `min_para_len`（默认 20 字）并入上一段。
→ docx 里用软换行排版的多段会被并成一段，影响逐段粒度；必要时先转成"段间空一行"。

## 交叉验证：一条命令（**推荐入口**）

单引擎结论不可信（同句可差 57 倍，见 `references/measured.md`）。用自带脚本固化这一步：

```bat
:: 脚本在技能目录里，不在仓库下，所以先用绝对路径定位（cwd 无关）
set S=%USERPROFILE%\.skills-manager\skills\autoaigc\scripts\aigc_cross.py

:: 默认 aigc_zh_v3 + simpleai 两个分类器交叉
python "%S%" 论文.docx

:: 三引擎 / 出 Markdown 报告 / 有分歧时退出码 2
python "%S%" 论文.docx --engines aigc_zh_v3,simpleai,zh_perplexity --md 报告.md --strict

:: 批量体检一个目录
python "%S%" --batch 论文目录 --md 汇总.md

:: 只验环境
python "%S%" --self-check
```

找不到 aigc.cmd 时脚本会依次试 `--cli`、`AIGC_CLI`、当前目录上溯、已知安装位置。

脚本输出：段级表（各引擎 prob + 判定）、篇级 AI 率、`⚠歧义` 段标红、一句人话结论。

**重要**：脚本把困惑度类引擎标为「参考」并从"两把尺子"判断里剔除 —— `zh_perplexity` 的 prob 不是概率，拉进来比较只会制造假分歧。

### 手工等价（没有 Python 时）

```bat
aigc.cmd detect -f 论文.docx --engine aigc_zh_v3 --json > a.json
aigc.cmd detect -f 论文.docx --engine simpleai   --json > b.json
```

`|pa - pb| >= 0.3` 的段**必须人工看一眼** —— 那是判据打架的地方，也最容易误伤真人文风。

## `--json` 契约（照字段读，别猜）

```jsonc
{
  "engine": "aigc_zh_v3", "engine_name": "AIGC 中文检测 v3",
  "threshold": 0.56, "file": "论文.docx",
  "paragraphs_total": 3, "suspicious": 2, "ai_ratio": 0.7279,
  "paragraphs": [{"index":1,"prob":0.9997,"len":128,
                  "suspicious":true,"advice":"saturated"}],
  "advice": {"level":"saturated","saturated":2,"note":"…"}
}
```

### 两个最容易读错的

- **`ai_ratio` 是「疑似段的字数」占全文比例，不是段数比例。** 3 段里 2 段疑似 ≠ 66.7%。
- **`suspicious` 用 `threshold` 判**（默认 **0.56**，读 `settings.json`，不是 0.5）。

## 该不该动手：看 `advice`

| `advice` | 条件 | 怎么办 |
|---|---|---|
| `clean` | prob < 阈值 | 不用改 |
| `amendable` | 阈值 ≤ prob < 0.85 | `rewrite` 有机会，改完复检 |
| `mixed` | 一部分 ≥ 0.99 | **只改不饱和的那些**，饱和段别浪费时间 |
| `saturated` | prob ≥ 0.99 | 规则改不动，必须重写语域 |

### 饱和段的天花板

（`references/measured.md` 第 3 节）：同一段 0.9997 起，同义替换 / 全 pass / 拆长句 / 加细节 / `--plain` 全部落在 0.98–0.9997，**过不了阈值**；只有整体口语化能到 0.0249。

这个模型认**语域**，不认词、不认句长、不认细节。

→ 别承诺"命令行一键降到 5%"，那是 LLM 或人工的活。
