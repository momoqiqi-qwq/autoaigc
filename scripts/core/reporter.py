# -*- coding: utf-8 -*-
"""输出渲染：终端文本表与 Markdown 报告。"""
from __future__ import annotations

from .analyzer import verdict


def _w(s: str) -> int:
    """中文按 2 列宽算，便于表格对齐。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)


def _pad(s: str, width: int) -> str:
    """按显示宽度补齐空格。"""
    return s + " " * max(0, width - _w(s))


def _foot_item(c: dict, eng: str) -> str:
    """篇级摘要里的单个引擎：名字 + 参考标记 + AI 率 + 近恒值警告。"""
    name = c["engines_name"].get(eng) or eng
    tag = "" if (c.get("role") or {}).get(eng) == "classifier" else "（参考）"
    sp = (c.get("seg_spread") or {}).get(eng)
    warn = f"[段间极差仅{sp:.2f}]" if sp is not None and sp < 0.02 else ""
    return f"{name}{tag}{'' if tag else ' '}{c['ai_ratio'][eng] * 100:.1f}%{warn}"


def render_text(c: dict, title: str) -> str:
    """渲染为纯文本表格（终端输出）。"""
    engs = c["engines"]
    head = ["段", "字数", *[c["engines_name"][e] or e for e in engs], "判定"]
    rows = []

    for s in c["segments"]:
        cells = [str(s["index"]), str(s["len"] or "-")]
        cells += [f"{s['probs'][e]:.4f}" for e in engs]
        if not s["unanimous"]:
            cells.append("⚠歧义")
        elif s["suspect"]:
            cells.append("疑似")
        else:
            cells.append("安全")
        rows.append(cells)

    widths = [max(_w(r[i]) for r in [head, *rows]) for i in range(len(head))]
    out = [f"## {title}", ""]
    out.append("  ".join(_pad(h, widths[i]) for i, h in enumerate(head)))
    out.append("  ".join("-" * widths[i] for i in range(len(head))))
    for r in rows:
        out.append("  ".join(_pad(v, widths[i]) for i, v in enumerate(r)))

    out.append("")
    foot = " / ".join(_foot_item(c, e) for e in engs)
    out.append(
        f"篇级：{foot}"
        f"  （阈值 {c['threshold']}，疑似 {c['suspect_segments']}/{c['paragraphs_total']} 段，"
        f"分歧 {c['disagree_segments']} 段）"
    )
    v, why = verdict(c)
    out.append(f"结论：{v} —— {why}")
    return "\n".join(out)


def render_markdown(c: dict, title: str, source: str) -> str:
    """渲染为 Markdown 表格（报告文件）。"""
    engs = c["engines"]
    lines = [f"### {title}", ""]
    lines.append(f"- 来源：`{source}`")
    lines.append("- 引擎与 AI 率：" + " / ".join(_foot_item(c, e) for e in engs))
    lines.append(f"- 阈值：{c['threshold']}")
    v, why = verdict(c)
    lines.append(f"- 结论：**{v}** —— {why}")
    lines.append("")

    header = "| 段 | 字数 | " + " | ".join(
        c["engines_name"][e] or e for e in engs
    ) + " | 判定 |"
    lines.append(header)
    lines.append("|---:|---:|" + "---:|" * len(engs) + "---|")

    for s in c["segments"]:
        mark = "⚠ 歧义" if not s["unanimous"] else ("疑似" if s["suspect"] else "安全")
        lines.append(
            f"| {s['index']} | {s['len'] or '-'} | "
            + " | ".join(f"{s['probs'][e]:.4f}" for e in engs)
            + f" | {mark} |"
        )

    lines.append("")
    return "\n".join(lines)
