#!/usr/bin/env python3
"""Render issues/issues.yaml -> issues/ISSUES.md and report/generated/issues_*.tex"""
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["Critical", "High", "Medium", "Low"]


def tex(s: str) -> str:
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    out = "".join(rep.get(c, c) for c in s)
    # allow line breaks inside long identifiers / paths / test ids
    for ch in (r"\_", "/", "::", "."):
        out = out.replace(ch, ch + r"\allowbreak{}")
    return out


def main():
    data = yaml.safe_load((ROOT / "issues" / "issues.yaml").read_text(encoding="utf-8"))
    meta, issues = data["meta"], data["issues"]
    counts = Counter(i["severity"] for i in issues)

    # ---- Markdown
    md = ["# OsdagBridge - Issue Register", "",
          f"Target: {meta['repository']} @ `{meta['commit']}` ({meta['commit_date']})  ",
          f"Environment: Python {meta['python']}, pytest {meta['pytest']}, {meta['os']}", "",
          "| Severity | Count |", "|---|---|"]
    md += [f"| {s} | {counts.get(s, 0)} |" for s in ORDER] + [f"| **Total** | **{len(issues)}** |", ""]
    md += ["| ID | Severity | Component | Title |", "|---|---|---|---|"]
    md += [f"| {i['id']} | {i['severity']} | {i['component']} | {i['title']} |" for i in issues] + [""]
    for i in issues:
        md += [f"## {i['id']} - {i['title']}", "",
               f"**Severity:** {i['severity']} | **Component:** {i['component']}", "",
               "**Steps to reproduce**", "", i["steps"].rstrip(), "",
               f"**Expected:** {i['expected']}", "", f"**Actual:** {i['actual']}", "",
               f"**Covered by:** {i['tests']}", "", f"**Suggested fix:** {i['fix']}", "", "---", ""]
    (ROOT / "issues" / "ISSUES.md").write_text("\n".join(md), encoding="utf-8")

    # ---- LaTeX
    gen = ROOT / "report" / "generated"
    gen.mkdir(parents=True, exist_ok=True)
    rows = [rf"{i['id'][6:]} & {i['severity']} & {tex(i['component'])} & {tex(i['title'])} \\" for i in issues]
    (gen / "issues_table.tex").write_text(
        "\\begin{longtable}{@{}p{0.9cm}p{1.5cm}p{2.6cm}p{8.2cm}@{}}\n"
        "\\toprule\n\\textbf{ID} & \\textbf{Sev.} & \\textbf{Component} & \\textbf{Finding}\\\\\n\\midrule\n\\endhead\n"
        + "\n".join(rows) + "\n\\bottomrule\n\\end{longtable}\n", encoding="utf-8")
    (gen / "issues_counts.tex").write_text(
        "\\begin{tabular}{@{}lr@{}}\n\\toprule\n\\textbf{Severity} & \\textbf{Findings}\\\\\n\\midrule\n"
        + "\n".join(f"{s} & {counts.get(s, 0)} \\\\" for s in ORDER)
        + f"\n\\midrule\n\\textbf{{Total}} & \\textbf{{{len(issues)}}}\\\\\n\\bottomrule\n\\end{{tabular}}\n", encoding="utf-8")
    # detailed entries for the appendix
    ent = []
    for i in issues:
        ent.append(f"\\subsection*{{ISSUE-{i['id'][6:]}: {tex(i['title'])}}}\n"
                   f"\\textbf{{Severity:}} {i['severity']}\\quad \\textbf{{Component:}} {tex(i['component'])}\\par\n"
                   f"\\textbf{{Steps to reproduce.}} {tex(' '.join(i['steps'].split()))}\\par\n"
                   f"\\textbf{{Expected.}} {tex(i['expected'])}\\par\n"
                   f"\\textbf{{Actual.}} {tex(i['actual'])}\\par\n"
                   f"\\textbf{{Covered by.}} {tex(i['tests'])}\\par\n"
                   f"\\textbf{{Suggested fix.}} {tex(i['fix'])}\n")
    (gen / "issues_detail.tex").write_text("\n".join(ent), encoding="utf-8")
    print(f"rendered {len(issues)} issues:", dict(counts))


if __name__ == "__main__":
    sys.exit(main())
