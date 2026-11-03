#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aigc_cross.py — 本地 AIGC 率多引擎交叉验证 / 批量体检

不依赖第三方库，只调用 aigc.cmd 的 --json 输出。
为什么需要它：本机三个检测模型对同一句给出 0.9992 / 0.0174 / 0.1500（差 57 倍、结论相反），
单引擎结论不可信。这个脚本把"至少交叉两个引擎"固化成一条命令。

用法
    python aigc_cross.py 论文.docx
    python aigc_cross.py 论文.docx --engines aigc_zh_v3,simpleai,zh_perplexity
    python aigc_cross.py 论文.docx --md 报告.md
    python aigc_cross.py --batch 论文目录 --md 汇总.md
    python aigc_cross.py --self-check            # 只验证 CLI 与环境

退出码
    0  正常
    1  出错（CLI 找不到 / 解析失败 / 全部引擎失败）
    2  有段落存在引擎分歧（--strict 时才作为失败）
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# 核心模块
from core import find_cli, run_detect, cross, verdict, render_text, render_markdown
from core.config import DEFAULT_ENGINES


def analyse(cli: Path, target: Path | str, engines: list[str],
            extra: list[str] | None = None, verbose: bool = True) -> dict:
    """对单个文件执行多引擎交叉验证。

    Args:
        cli: aigc.cmd 路径
        target: 要检测的文件或文本
        engines: 引擎列表
        extra: 额外参数
        verbose: 是否输出进度

    Returns:
        交叉分析结果

    Raises:
        RuntimeError: 所有引擎都失败
    """
    results, errors = [], []
    for eng in engines:
        if verbose:
            print(f"  跑 {eng} …", file=sys.stderr, flush=True)
        try:
            results.append(run_detect(cli, target, eng, extra))
        except Exception as exc:
            errors.append(f"{eng}: {exc}")
            if verbose:
                print(f"    ! {exc}", file=sys.stderr, flush=True)

    for e in errors:
        print(f"[warn] 跳过 {e}", file=sys.stderr)

    if not results:
        raise RuntimeError("所有引擎都失败了，检查 aigc.cmd doctor / engines")

    if len(results) == 1:
        print(
            f"[warn] 只剩 {results[0]['_engine']} 一个引擎，"
            "单引擎结论不可信（同句可差 57 倍）",
            file=sys.stderr
        )

    return cross(results)


def main(argv: list[str] | None = None) -> int:
    """主流程：解析参数并执行检测。"""
    ap = argparse.ArgumentParser(
        description="本地 AIGC 率多引擎交叉验证 / 批量体检"
    )
    ap.add_argument("file", nargs="?", help="txt/md/docx/pdf")
    ap.add_argument("--batch", metavar="DIR", help="批量体检一个目录")
    ap.add_argument(
        "--engines",
        default=",".join(DEFAULT_ENGINES),
        help=f"逗号分隔，默认 {','.join(DEFAULT_ENGINES)}"
    )
    ap.add_argument("--cli", help="aigc.cmd 路径（默认自动查找）")
    ap.add_argument("--md", metavar="OUT.md", help="输出/追加 Markdown 报告")
    ap.add_argument("--json", action="store_true", help="stdout 只出 JSON")
    ap.add_argument("--strict", action="store_true", help="有引擎分歧时退出码 2")
    ap.add_argument("--self-check", action="store_true", help="只验证环境")
    args = ap.parse_args(argv)

    cli = find_cli(args.cli)
    engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    extra = ["--gpu"] if os.environ.get("AIGC_GPU") == "1" else None

    # 自检模式
    if args.self_check:
        from core.detector import _extract_json

        print(f"CLI: {cli}")
        p = subprocess.run(
            [str(cli), "doctor", "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        ok = p.returncode == 0
        print(f"doctor 退出码 {p.returncode}")
        if ok:
            try:
                d = _extract_json(p.stdout)
                n_models = len(d.get("models_on_disk") or [])
                print(
                    f"python {d.get('python')} / torch {d.get('torch_version')} / "
                    f"cuda {d.get('cuda')} / 实现 {len(d.get('impls') or [])} 个 / "
                    f"已下模型 {n_models} / 默认引擎 {d.get('default_detect_engine')}"
                )
            except Exception:
                pass
        return 0 if ok else 1

    if not args.file and not args.batch:
        ap.error("要么给一个文件，要么 --batch 一个目录")

    # 批量模式
    if args.batch:
        root = Path(args.batch)
        if not root.is_dir():
            print(f"[x] 不是目录: {root}", file=sys.stderr)
            return 1
        files = sorted(
            p for p in root.iterdir()
            if p.suffix.lower() in {".txt", ".md", ".docx", ".pdf"}
        )
        if not files:
            print(f"[x] {root} 下没有 txt/md/docx/pdf", file=sys.stderr)
            return 1

        print(
            f"批量 {len(files)} 篇 × {len(engines)} 引擎"
            f"（每篇每引擎冷启约 10~13s）",
            file=sys.stderr
        )

        rows, chunks = [], []
        for f in files:
            try:
                c = analyse(cli, f, engines, extra)
                v, _ = verdict(c)
                rows.append({
                    "file": f.name,
                    **{e: round(c["ai_ratio"][e], 4) for e in c["engines"]},
                    "suspect": c["suspect_segments"],
                    "disagree": c["disagree_segments"],
                    "verdict": v,
                })
                chunks.append(render_markdown(c, f.name, str(f)))
                print(f"  {f.name}: {v}", file=sys.stderr)
            except Exception as exc:
                rows.append({"file": f.name, "verdict": f"失败 {exc}"})
                print(f"  {f.name}: 失败 {exc}", file=sys.stderr)

        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(f"\n## 批量汇总（{len(files)} 篇）\n")
            print("| 文件 | AI率(" + "/".join(engines) + ") | 疑似段 | 分歧 | 结论 |")
            print("|---|---|---:|---:|---|")
            for r in rows:
                vals = " / ".join(str(r.get(e, "-")) for e in engines)
                print(
                    f"| {r['file']} | {vals} | {r.get('suspect', '-')} "
                    f"| {r.get('disagree', '-')} | {r['verdict']} |"
                )

        if args.md:
            Path(args.md).write_text(
                "# AIGC 率批量体检\n\n" + "\n".join(chunks),
                encoding="utf-8"
            )
            print(f"\n报告 → {args.md}", file=sys.stderr)

        bad = sum(1 for r in rows if r.get("disagree"))
        return 2 if (args.strict and bad) else 0

    # 单篇模式
    target = Path(args.file)
    if not target.is_file():
        print(f"[x] 文件不存在: {target}", file=sys.stderr)
        return 1

    print(f"交叉验证 {target.name} × {len(engines)} 引擎", file=sys.stderr)
    try:
        c = analyse(cli, target, engines, extra)
    except Exception as exc:
        print(f"[x] {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(c, ensure_ascii=False, indent=2))
    else:
        print(render_text(c, target.name))

    if args.md:
        md = render_markdown(c, target.name, str(target))
        Path(args.md).write_text("# AIGC 率交叉验证\n\n" + md, encoding="utf-8")
        print(f"\n报告 → {args.md}", file=sys.stderr)

    return 2 if (args.strict and c["disagree_segments"]) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n中断", file=sys.stderr)
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[x] {exc}", file=sys.stderr)
        sys.exit(1)
