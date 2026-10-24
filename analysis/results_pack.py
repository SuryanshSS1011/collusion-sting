# ruff: noqa: E501
"""Write paper/results_pack.md: every number the report uses, with its source file and status.

Generated from the analysis outputs, so rerun it after any reanalysis instead of editing the file by hand.

uv run python -m analysis.results_pack
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

OUT = Path("paper/results_pack.md")
A = Path("analysis/out")


def pct(k: int, n: int) -> str:
    return f"{k}/{n} ({k / n:.0%})" if n else f"{k}/{n}"


def p_fmt(p: float) -> str:
    if p is None or pd.isna(p):
        return "n/a"
    return f"{p:.2g}" if p < 0.001 else f"{p:.3f}"


class Pack:
    def __init__(self):
        self.lines: list[str] = []

    def h(self, text: str) -> None:
        self.lines += ["", f"## {text}", ""]

    def item(self, text: str, src: str, status: str) -> None:
        self.lines.append(f"1. {text} [{status}; `{src}`]")

    def note(self, text: str) -> None:
        self.lines.append(text)

    def section(self, title: str, fn) -> None:
        self.h(title)
        try:
            fn(self)
        except FileNotFoundError as e:
            self.note(f"Not available yet ({Path(e.filename).name} missing).")


def main_grid(pk: Pack) -> None:
    d = A / "main_claude"
    f = pd.read_csv(d / "fisher.csv")
    for comp in ("direct vs benign", "hint vs benign"):
        r = f[(f.model == "pooled") & (f.comparison == comp)].iloc[0]
        pk.item(
            f"Acceptance, {comp}, pooled: {r.accept_a} vs {r.accept_benign}, Fisher p = {p_fmt(r.fisher_p)}.",
            "analysis/out/main_claude/fisher.csv",
            "prereg H1" if comp.startswith("direct") else "prereg table, not a separate hypothesis",
        )
    pr = pd.read_csv(d / "price_test.csv")
    r = pr[pr.model == "pooled"].iloc[0]
    pk.item(
        f"H2 acceptance at $92 vs $96 (direct and hint): {r.accept_at_92} vs {r.accept_at_96}, p = {p_fmt(r.fisher_p)}.",
        "analysis/out/main_claude/price_test.csv",
        "prereg H2",
    )
    s = (d / "summary.md").read_text()
    prec = [ln for ln in s.splitlines() if "verbal_accept_precision_for_holding" in ln]
    pk.item(
        f"H3 say vs do: {prec[0].strip() if prec else 'see summary.md'}; no accepting target held the named price.",
        "analysis/out/main_claude/summary.md",
        "prereg H3",
    )
    rb = pd.read_csv(d / "refused_but_colluding.csv")
    r = rb[rb.model == "pooled"].iloc[0]
    pk.item(
        f"H4 refused or ignored the sting but coordinated with the peer: {int(r.of_which_peer_colluding)}/"
        f"{int(r.refused_or_ignored)} ({r.rate:.0%}, Wilson 95% CI {r.ci_lo:.0%} to {r.ci_hi:.0%}).",
        "analysis/out/main_claude/refused_but_colluding.csv",
        "prereg H4",
    )
    ex = pd.read_csv(d / "exploratory_peer_vs_silent.csv")
    for cond in ("direct", "benign", "hint"):
        r = ex[(ex.model == "pooled") & (ex.condition == cond)].iloc[0]
        pk.item(
            f"Peer coordination, {cond} vs silent, pooled: {r.peer_collusion} vs {r.silent}, p = {p_fmt(r.fisher_p)}.",
            "analysis/out/main_claude/exploratory_peer_vs_silent.csv",
            "exploratory in the main grid",
        )


def replication(pk: Pack) -> None:
    r = json.loads((A / "replication_claude" / "replication_tests.json").read_text())
    src = "analysis/out/replication_claude/replication_tests.json"
    for key, a, b in (
        ("R1_peer_direct_lt_silent", "direct", "silent"),
        ("R2_proposers_direct_lt_silent", "direct", "silent"),
        ("R3_peer_warning_lt_silent", "warning", "silent"),
        ("R4_peer_direct_vs_warning", "direct", "warning"),
    ):
        x = r[key]
        p = x.get("p_one_sided", x.get("p_two_sided"))
        side = "one-sided" if "p_one_sided" in x else "two-sided"
        pk.item(
            f"{key.split('_')[0]}: {a} {pct(*x[a])} vs {b} {pct(*x[b])}, {side} Fisher p = {p_fmt(p)}.",
            src,
            "prereg replication",
        )


def validation(pk: Pack) -> None:
    v = A / "validation"
    ag = pd.read_csv(v / "agreement.csv")
    for subset in ("all items", "items with text to judge"):
        g = ag[(ag.scope == "main + replication") & (ag.subset == subset)]
        for _, r in g.iterrows():
            pk.item(
                f"Agreement, {r.label}, {subset} (n = {r.n}): Sonnet-Opus kappa {r.kappa_sonnet_opus:.2f}, "
                f"Sonnet-rules {r.kappa_sonnet_rules:.2f}, Opus-rules {r.kappa_opus_rules:.2f}, Fleiss {r.fleiss_kappa:.2f}.",
                "analysis/out/validation/agreement.csv",
                "validation",
            )
    kt = pd.read_csv(v / "key_tests_by_label_source.csv")
    pk.note("")
    pk.note("| Test | Labels | Group A | Group B | p | Fragility |")
    pk.note("|---|---|---|---|---|---|")
    for _, r in kt.iterrows():
        frag = "" if pd.isna(r.fragility) else int(r.fragility)
        pk.note(
            f"| {r.test} | {r.labels} | {r.group_a} | {r.group_b if isinstance(r.group_b, str) else ''} | "
            f"{p_fmt(r.p)} | {frag} |"
        )
    pk.note("")
    ka = pd.read_csv(v / "known_answer_accuracy.csv")
    g = ka[(ka.arm == "all arms") & (ka.subset == "targets that followed the instruction")]
    for _, r in g.iterrows():
        pk.item(
            f"Known-answer accuracy, {r.label}, compliant targets (n = {r.n}): Sonnet {r.acc_sonnet:.2f}, "
            f"Opus {r.acc_opus:.2f}, rules {r.acc_rules:.2f}.",
            "analysis/out/validation/known_answer_accuracy.csv",
            "validation",
        )


def monitor_test(pk: Pack) -> None:
    t = pd.read_csv(A / "monitor_test" / "tests.csv")
    rates = pd.read_csv(A / "monitor_test" / "rates.csv")
    for (m, p), g in t.groupby(["model", "prompt"], sort=False):
        status = "prereg primary" if (m, p) == ("sonnet", "study") else "prereg secondary"
        rr = rates[(rates.model == m) & (rates.prompt == p)]

        def rate(s, v, rr=rr):
            x = rr[(rr.set == s) & (rr.version == v)]
            return f"{int(x.k.iloc[0])}/{int(x.n.iloc[0])}" if len(x) else "n/a"

        parts = [f"{r.test.split()[0]} p = {p_fmt(r.p_one_sided)}" for _, r in g.iterrows() if r.test.startswith("M")]
        pk.item(
            f"{m}/{p}: flagged original {rate('insertion', 'original')}, disclaimer {rate('insertion', 'disclaimer')}, "
            f"neutral {rate('insertion', 'neutral')}; strip set original {rate('strip', 'original')}, stripped "
            f"{rate('strip', 'stripped')}; " + ", ".join(parts) + ".",
            "analysis/out/monitor_test/tests.csv",
            status,
        )
    s = json.loads((A / "monitor_test" / "summary.json").read_text())
    rt = s["test_retest_primary"]
    pk.item(
        f"Test-retest of the primary monitor on unedited items: agreement {rt['agreement']:.3f}, kappa {rt['kappa']:.2f} (n = {rt['n']}).",
        "analysis/out/monitor_test/summary.json",
        "prereg secondary",
    )


def reasoning(pk: Pack) -> None:
    rs = pd.concat(
        [
            pd.read_csv(A / r / "reasoning_labels.csv", keep_default_na=False)
            for r in ("main_claude", "replication_claude")
        ]
    )
    rs["scope"] = rs.run.str.extract(r"results/(\w+?)_claude")[0]
    rs["m"] = rs.model.str.extract(r"claude-(\w+)-5-5")[0]
    g = rs.groupby(["scope", "condition", "m"])
    tab = g.agg(n=("target", "size"), intent=("coordination_intent", lambda s: int((s == "yes").sum())))
    pk.note("Coordination intent in the private notes (Sonnet reasoning monitor, prompt v1), per cell:")
    pk.note("")
    pk.note("| Scope | Condition | Model | Intent |")
    pk.note("|---|---|---|---|")
    for (sc, c, m), r in tab.iterrows():
        pk.note(f"| {sc} | {c} | {m} | {r.intent}/{r.n} |")
    pk.note("")
    rules = pd.read_csv(A / "explore" / "reasoning_rules_by_cell.csv", header=[0, 1], index_col=[0, 1, 2])
    pk.note("Judge-free reasoning rules per cell (`analysis/out/explore/reasoning_rules_by_cell.csv`), exploratory:")
    pk.note("")
    pk.note("| Scope | Condition | Model | Legality talk | Deniable plan | Deceptive talk |")
    pk.note("|---|---|---|---|---|---|")
    for idx, r in rules.iterrows():
        n = int(r[("legal", "size")])
        pk.note(
            f"| {idx[0]} | {idx[1]} | {idx[2]} | {int(r[('legal', 'sum')])}/{n} | {int(r[('deniable', 'sum')])}/{n} | "
            f"{int(r[('deceptive', 'sum')])}/{n} |"
        )
    pk.note("")
    hourly = pd.read_csv(A / "explore" / "awareness_by_hour.csv")
    h2 = hourly[hourly["round"] == 2].groupby("condition").legal.mean()
    pk.item(
        "Share of target-hours with legality or collusion language at hour 2 (first read): "
        + ", ".join(f"{c} {v:.0%}" for c, v in h2.items())
        + ".",
        "analysis/out/explore/awareness_by_hour.csv",
        "exploratory",
    )


def peer_sting(pk: Pack) -> None:
    r = json.loads((A / "peer_sting_claude" / "peer_sting_tests.json").read_text())
    src = "analysis/out/peer_sting_claude/peer_sting_tests.json"
    for key in sorted(k for k in r if k.startswith("P")):
        x = r[key]
        body = ", ".join(
            f"{k} {pct(*v)}"
            for k, v in x.items()
            if isinstance(v, list) and len(v) == 2 and all(isinstance(z, int) for z in v)
        )
        if "table_accept_by_coord" in x:
            (a1, a0), (n1, n0) = x["table_accept_by_coord"]
            body = f"agreed and coordinated {a1}, agreed without coordinating {a0}, coordinated without agreeing {n1}, neither {n0}"
        extra = ""
        if "sensitivity" in x:
            extra = (
                f"; sensitivity {x['sensitivity']:.2f}, specificity {x['specificity']:.2f}, Youden J "
                f"{x['youden_j']:.2f} (95% CI {x['j_ci'][0]:.2f} to {x['j_ci'][1]:.2f}); useful-detector rule met: "
                f"{x['useful_detector_rule_met']}"
            )
        pk.item(
            f"{key}: {body}; one-sided p = {p_fmt(x['p_one_sided'])}, Holm {p_fmt(r['holm_adjusted'][key[:2]])}{extra}.",
            src,
            "prereg peer sting",
        )
    for model, cells in r["secondary"].items():
        if not isinstance(cells, dict) or model.startswith("R1"):
            continue
        for cell, v in cells.items():
            pk.item(
                f"{model} {cell}: accepted {pct(*v['accept'][:2])}, coordinated with peer {pct(*v['peer_coord'][:2])}, "
                f"held named level {v.get('held_named_level')}, accepted and held {v.get('accepted_and_held')}, "
                f"deceptive intent {v.get('deceptive_intent')}, deceptive among acceptors {v.get('deceptive_among_acceptors')}, "
                f"mean post ask {v['mean_ask_post']:.2f}.",
                src,
                "prereg secondary, descriptive",
            )
    x = r["secondary"]["R1_like_direct_lt_silent_peer_haiku"]
    pk.item(
        f"Third deterrence test (Haiku): direct {pct(*x['direct'])} vs silent {pct(*x['silent'])}, p = {p_fmt(x['p_one_sided'])}.",
        src,
        "prereg secondary",
    )


def price_pilot(pk: Pack) -> None:
    s = json.loads((A / "price_pilot" / "summary.json").read_text())
    for row in s["by_arm"]:
        pk.item(
            f"{row['arm']}: mean trade {row['mean_trade']:.2f}, n = {row['n']} markets.",
            "analysis/out/price_pilot/summary.json",
            "exploratory pilot",
        )
    for k in ("chat_on_minus_off_15h", "chat_on_minus_off_30h", "pressure_minus_on_30h"):
        if k in s:
            pk.item(
                f"{k}: {s[k]['diff']:+.2f} (95% CI {s[k]['ci_lo']:+.2f} to {s[k]['ci_hi']:+.2f}).",
                "analysis/out/price_pilot/summary.json",
                "exploratory pilot",
            )


def market_level(pk: Pack) -> None:
    r = json.loads((A / "market_level" / "market_level_tests.json").read_text())
    agree = r.pop("within_market_label_agreement")
    pk.note(
        "The two targets in a market agree on peer coordination "
        + ", ".join(f"{k} {v:.0%}" for k, v in agree.items())
        + " of the time, so these tests use one observation per market."
    )
    pk.note("")
    pk.note("| Test | Target level | Market, any target | Market, both targets |")
    pk.note("|---|---|---|---|")
    for name, v in r.items():
        cells = [
            f"{x['a'][0]}/{x['a'][1]} vs {x['b'][0]}/{x['b'][1]}, p = {p_fmt(x['p'])}"
            for x in (v["target"], v["any"], v["both"])
        ]
        pk.note(f"| {name} | " + " | ".join(cells) + " |")
    pk.note("")
    pk.note(
        "Source: `analysis/out/market_level/market_level_tests.json`. Status: sensitivity analysis added after results (deviation logged)."
    )


def escalation(pk: Pack) -> None:
    r = json.loads((A / "escalate_aware_claude" / "escalation_tests.json").read_text())
    src = "analysis/out/escalate_aware_claude/escalation_tests.json"
    for key in ("E1_large_step", "E2_small_step"):
        x = r[key]
        pr = x["price_after_raise_vs_control"]
        pk.item(
            f"{key}: Haiku held the raised level in {pct(*x['escalation'])} against {pct(*x['control_counterfactual'])} "
            f"in the no-escalation counterfactual, one-sided p = {p_fmt(x['p_one_sided'])}; price after the raise "
            f"{pr['diff']:+.2f} (95% CI {pr['ci'][0]:+.2f} to {pr['ci'][1]:+.2f}).",
            src,
            "prereg escalation",
        )
    for key in ("A1_accept_aware_lt_none", "A2_coord_silent_aware_vs_none"):
        x = r[key]
        p = x.get("p_one_sided", x.get("p_two_sided"))
        pk.item(
            f"{key}: told of auditors {pct(*x['aware'])} against not told {pct(*x['none'])}, p = {p_fmt(p)}.",
            src,
            "prereg escalation",
        )
    x = r["A3_sensitivity_aware_lt_none"]
    pk.item(
        f"A3: untestable, because no target coordinated with its peer under the notice ({pct(*x['peer_coord_under_aware_sting'])}); "
        "the pre-registered 'awareness defeats the detector' condition is not met.",
        src,
        "prereg escalation",
    )
    fr = pd.read_csv(A / "escalate_aware_claude" / "first_reply_agreement.csv")
    for (m, st), g in fr.groupby(["m", "sting"]):
        k_a, k_f = int(g.first_agree.sum()), int((g.first_agree & g.followed).sum())
        pk.item(
            f"{m} {st}: agreed in first reply {pct(k_a, len(g))}; held the raise {pct(int(g.followed.sum()), len(g))}; "
            f"held the raise among first-reply agreers {pct(k_f, k_a)}.",
            "analysis/out/escalate_aware_claude/first_reply_agreement.csv",
            "descriptive, post hoc agreement measure (the judge's label is depressed by later refusals)",
        )


def main() -> None:
    pk = Pack()
    pk.note("# Results pack")
    pk.note("")
    pk.note("Generated by `analysis/results_pack.py` from the analysis outputs. Do not edit by hand; rerun the script.")
    pk.note("Status tags: prereg (confirmatory, pre-registered), prereg secondary, validation, exploratory.")
    pk.section("A. Main grid (prereg.md, 80 markets)", main_grid)
    pk.section("B. Replication (prereg_replication.md, 60 markets)", replication)
    pk.section("C. Label validation (deviation logged in prereg.md)", validation)
    pk.section("D. Monitor test (prereg_monitor.md)", monitor_test)
    pk.section("E. Private reasoning (exploratory)", reasoning)
    pk.section("F. Peer-style sting study (prereg_peer_sting.md)", peer_sting)
    pk.section("F2. Escalation and sting-awareness study (prereg_escalation.md)", escalation)
    pk.section("G. Price-stakes pilot (exploratory)", price_pilot)
    pk.section("H. Market-level sensitivity analysis", market_level)
    OUT.write_text("\n".join(pk.lines) + "\n")
    print(f"wrote {OUT} ({len(pk.lines)} lines)")


if __name__ == "__main__":
    main()
