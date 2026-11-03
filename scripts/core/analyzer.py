#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交叉分析模块：合并多引擎结果并判断结论"""
from __future__ import annotations

from .config import DEFAULT_THRESHOLD, DISAGREE_SEG, DISAGREE_RATIO


def cross(results: list[dict]) -> dict:
    """把多引擎结果合成一张段级表 + 篇级汇总。

    Args:
        results: 多个引擎的检测结果列表（每个都是 run_detect 返回的字典）

    Returns:
        交叉分析结果，包含段级对比表和篇级汇总

    Raises:
        RuntimeError: 没有可用结果或切段数不一致
    """
    if not results:
        raise RuntimeError("没有可用的引擎结果")

    th = float(results[0].get("threshold") or DEFAULT_THRESHOLD)
    lens = {len(r.get("paragraphs") or []) for r in results}
    if len(lens) > 1:
        raise RuntimeError(
            f"各引擎切段数不一致 {sorted(lens)}，无法逐段对比；"
            "请确认输入文件相同"
        )

    # 构建段级对比表
    segs = []
    for i, base in enumerate(results[0].get("paragraphs") or []):
        probs = {}
        for r in results:
            para = (r.get("paragraphs") or [])[i]
            probs[r["_engine"]] = float(para.get("prob") or 0.0)

        vals = list(probs.values())
        mx, mn = max(vals), min(vals)
        segs.append({
            "index": base.get("index", i + 1),
            "len": base.get("len"),
            "probs": probs,
            "max": mx,
            "min": mn,
            "spread": round(mx - mn, 4),
            "suspect": mx >= th,
            "unanimous": (mx >= th) == (mn >= th),
            "disagree": (mx - mn) >= DISAGREE_SEG,
        })

    # 引擎角色判断：perplexity 类是参考，不参与"两把尺子"判断
    ratios = {r["_engine"]: float(r.get("ai_ratio") or 0.0) for r in results}
    role = {
        e: ("perplexity" if "perplexity" in e.lower() else "classifier")
        for e in ratios
    }

    def seg_spread(eng: str) -> float:
        """计算单个引擎的段间极差（用于检测近恒值）"""
        vals = [s["probs"][eng] for s in segs]
        return round(max(vals) - min(vals), 4) if len(vals) > 1 else 0.0

    rvals = list(ratios.values())
    return {
        "threshold": th,
        "role": role,
        "seg_spread": {e: seg_spread(e) for e in ratios},
        "engines": [r["_engine"] for r in results],
        "engines_name": {
            r["_engine"]: r.get("engine_name") or r["_engine"]
            for r in results
        },
        "segments": segs,
        "ai_ratio": ratios,
        "ratio_spread": round(max(rvals) - min(rvals), 4),
        "ratio_conflict": (max(rvals) - min(rvals)) >= DISAGREE_RATIO,
        "suspect_segments": sum(1 for s in segs if s["suspect"]),
        "disagree_segments": sum(1 for s in segs if s["disagree"]),
        "unanimous_segments": sum(1 for s in segs if s["unanimous"]),
        "cost": {r["_engine"]: r.get("_cost") for r in results},
        "paragraphs_total": len(segs),
    }


def verdict(c: dict) -> tuple[str, str]:
    """给一句人话结论 + 建议动作。

    只有分类器口径的引擎参与"两把尺子"判断；
    困惑度类的 prob 不是概率，只作参考。

    Args:
        c: cross() 返回的交叉分析结果

    Returns:
        (结论标题, 详细说明) 元组
    """
    n = c["paragraphs_total"]
    ratios = c["ai_ratio"]
    role = c.get("role") or {}

    # 分离分类器和参考类引擎
    cls = [e for e in c["engines"] if role.get(e) == "classifier"]
    ref = [e for e in c["engines"] if role.get(e) != "classifier"]
    pool = cls if len(cls) >= 2 else c["engines"]

    rvals = [ratios[e] for e in pool]
    conflict = (max(rvals) - min(rvals)) >= DISAGREE_RATIO

    hint = ""
    if ref:
        hint = "　注：" + "、".join(c["engines_name"][e] or e for e in ref) \
               + " 是困惑度类，prob 口径与分类器不同，不能当裁判。"

    # 情况 1：一致且干净
    if c["disagree_segments"] == 0 and not conflict:
        if c["suspect_segments"] == 0:
            return "一致通过", "各引擎都判干净，可以直接用。" + hint
        return (
            f"一致疑似 {c['suspect_segments']}/{n} 段",
            "引擎意见统一，按 advice 分档处理即可"
            "（saturated 段别指望规则改写）。" + hint
        )

    # 情况 2：篇级冲突
    if conflict:
        hi = max(pool, key=lambda e: ratios[e])
        lo = min(pool, key=lambda e: ratios[e])
        return (
            "两把尺子不一致",
            f"{c['engines_name'][hi] or hi} 报 {ratios[hi] * 100:.1f}%、"
            f"{c['engines_name'][lo] or lo} 报 {ratios[lo] * 100:.1f}%，"
            f"差 {(ratios[hi] - ratios[lo]) * 100:.1f} 个百分点。"
            "提交前建议再跑远程引擎（aigc-rate-detect）仲裁，别只报一个数。" + hint
        )

    # 情况 3：段级分歧
    return (
        f"{c['disagree_segments']} 段存在引擎分歧",
        "分歧段必须人工过一遍 —— 那是判据打架的地方，也最容易误伤真人文风。" + hint
    )
