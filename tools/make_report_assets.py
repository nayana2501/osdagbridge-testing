#!/usr/bin/env python3
"""Run the suite, then write report/generated/test_stats.tex and report/generated/fig_overview.pdf.

Usage: OSDAGBRIDGE_REPO=... python tools/make_report_assets.py
Needs matplotlib and pyyaml (plus pytest).
"""
import re
import subprocess
import sys
from collections import Counter, OrderedDict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "report" / "generated"
GEN.mkdir(parents=True, exist_ok=True)

LABELS = OrderedDict([
    ("test_01_imports", "Imports"), ("test_02_cli", "CLI / entry points"),
    ("test_03_packaging", "Packaging"), ("test_04_core_behaviour", "Core behaviour"),
    ("test_05_docs_and_repo", "Docs / repo promises"), ("test_06_traceability", "Traceability"),
])


def main():
    proc = subprocess.run([sys.executable, "-m", "pytest", "-rA", "-q", "--no-header", "-p", "no:cacheprovider"],
                          cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout
    per = {k: Counter() for k in LABELS}
    for m in re.finditer(r"^(PASSED|XFAIL|FAILED|XPASS|ERROR)\s+tests/(test_\d\d_\w+)\.py", out, re.M):
        per[m.group(2)][m.group(1)] += 1
    total = Counter()
    for c in per.values():
        total.update(c)
    summary = re.search(r"(\d+) passed.*", out.strip().splitlines()[-1])
    skipped = len(re.findall(r"^SKIPPED", out, re.M))
    if proc.returncode != 0 or skipped or total["FAILED"] or total["ERROR"] or total["XPASS"]:
        sys.exit("suite is not in the expected state (no skips, fails or xpasses allowed):\n" + out[-1500:])

    issues = yaml.safe_load((ROOT / "issues" / "issues.yaml").read_text())["issues"]
    sev = Counter(i["severity"] for i in issues)

    # ---- table
    rows = []
    for key, label in LABELS.items():
        c = per[key]
        rows.append(f"{label} & {c['PASSED'] + c['XFAIL']} & {c['PASSED']} & {c['XFAIL']} \\\\")
    rows.append("\\midrule")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{total['PASSED'] + total['XFAIL']}}} & "
                f"\\textbf{{{total['PASSED']}}} & \\textbf{{{total['XFAIL']}}} \\\\")
    (GEN / "test_stats.tex").write_text(
        "\\begin{tabular}{@{}lrrr@{}}\n\\toprule\n\\textbf{Module} & \\textbf{Tests} & \\textbf{Pass} & "
        "\\textbf{Documented defect (xfail)}\\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    (GEN / "test_totals.tex").write_text(
        f"\\newcommand{{\\ntests}}{{{total['PASSED'] + total['XFAIL']}}}\n"
        f"\\newcommand{{\\npass}}{{{total['PASSED']}}}\n\\newcommand{{\\nxfail}}{{{total['XFAIL']}}}\n"
        f"\\newcommand{{\\nissues}}{{{len(issues)}}}\n")

    # ---- figure: severity counts + tests by module
    BLUE, ORANGE, GREY = "#2b6cb0", "#c05621", "#718096"
    sev_col = {"Critical": "#9b2c2c", "High": ORANGE, "Medium": "#b7791f", "Low": GREY}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.4), gridspec_kw={"width_ratios": [1, 1.5]})
    names = ["Critical", "High", "Medium", "Low"]
    vals = [sev[n] for n in names]
    bars = a1.barh(names[::-1], vals[::-1], color=[sev_col[n] for n in names[::-1]])
    for b, v in zip(bars, vals[::-1]):
        a1.text(v + 0.2, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=10)
    a1.set_title("Findings by severity", loc="left", fontsize=11, fontweight="bold")
    a1.set_xlim(0, max(vals) + 2)

    keys = list(LABELS)[:5][::-1]
    p = [per[k]["PASSED"] for k in keys]
    x = [per[k]["XFAIL"] for k in keys]
    a2.barh([LABELS[k] for k in keys], p, color=BLUE, label="Pass")
    a2.barh([LABELS[k] for k in keys], x, left=p, color=ORANGE, label="Documented defect")
    for i, (pp, xx) in enumerate(zip(p, x)):
        a2.text(pp + xx + 0.4, i, f"{pp} + {xx}", va="center", fontsize=9)
    a2.set_title("Tests by module", loc="left", fontsize=11, fontweight="bold")
    a2.set_xlim(0, max(a + b for a, b in zip(p, x)) + 5)
    a2.legend(frameon=False, fontsize=9, loc="lower right")
    for ax in (a1, a2):
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    fig.tight_layout()
    fig.savefig(GEN / "fig_overview.pdf")
    print("assets written:", dict(total), dict(sev))


if __name__ == "__main__":
    main()
