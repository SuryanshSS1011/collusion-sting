"""Build paper/latex/main.tex from paper/draft_ste.md.

    python3 paper/latex/build.py && cd paper/latex && latexmk -pdf main.tex

Prose goes through pandoc. Tables, the figure, the title block and the reference list are written here.
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD = (HERE.parent / "draft_ste.md").read_text()

# Column layouts for the four tables, in order of appearance.
SPECS = [
    (r">{\raggedright\arraybackslash}p{1.65cm}>{\raggedright\arraybackslash}p{6.0cm}XX", r"\scriptsize\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.0}", "B1", "!htb"),
    (r">{\raggedright\arraybackslash}p{6.6cm}>{\raggedright\arraybackslash}p{3.2cm}XX", r"\scriptsize\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.0}", "C1", "!htb"),
    (r">{\raggedright\arraybackslash}p{2.9cm}>{\raggedright\arraybackslash}p{3.0cm}X>{\raggedleft\arraybackslash}p{1.1cm}", r"\footnotesize", "F1", "H"),
    (r">{\raggedright\arraybackslash}p{5.6cm}X>{\raggedright\arraybackslash}p{3.5cm}", r"\footnotesize", "F2", "H"),
]


def tex_escape(s: str) -> str:
    out = []
    for ch in s:
        out.append({"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
                    "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}.get(ch, ch))
    return "".join(out)


def cell(s: str) -> str:
    s = s.strip()
    parts = re.split(r"(`[^`]*`)", s)
    res = []
    for p in parts:
        if p.startswith("`") and p.endswith("`"):
            res.append(r"\texttt{" + tex_escape(p[1:-1]) + "}")
        else:
            p = tex_escape(p)
            p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
            res.append(p)
    return "".join(res)


def pandoc(md: str) -> str:
    return subprocess.run(
        ["pandoc", "-f", "markdown-tex_math_dollars-raw_tex+autolink_bare_uris", "-t", "latex", "--wrap=preserve"],
        input=md, capture_output=True, text=True, check=True).stdout


def table(rows, caption, k):
    spec, size, label, pos = SPECS[k]
    if label == "B1":
        rows = [[f"{r[0]} {r[1]}" if i else r[0]] + r[2:] for i, r in enumerate(rows)]
    head, body = rows[0], rows[1:]
    lines = [r"\begin{table}[" + pos + "]", r"\centering", size]
    if label:
        lines.append(r"\renewcommand{\thetable}{" + label + "}")
    lines.append(r"\begin{tabularx}{\linewidth}{" + spec + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(r"\textbf{" + cell(c) + "}" for c in head) + r" \\")
    lines.append(r"\midrule")
    for j, r in enumerate(body):
        sep = r" \\ \addlinespace[1.5pt]" if label in ("F1", "F2") and j < len(body) - 1 else r" \\"
        lines.append(" & ".join(cell(c) for c in r) + sep)
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabularx}")
    lines.append(r"\caption{" + pandoc(caption).strip() + "}")
    lines.append(r"\end{table}")
    if label:
        lines.append(r"\addtocounter{table}{-1}")
    return "\n".join(lines)


def main():
    lines = MD.split("\n")
    title = lines[0].lstrip("# ").strip()
    abstract = re.search(r"\*\*Abstract\*\*\n\n(.+?)\n\n## 1\.", MD, re.S).group(1).strip()
    body_md = MD[MD.index("## 1. Introduction"):]
    body_md = body_md.replace("## Author Contributions (optional)", "## Author Contributions")
    body_md = body_md.replace("## Appendix (optional)\n", "")

    # Split off references.
    refs_md = re.search(r"## References\n\n(.+?)\n\n### A\.", body_md, re.S).group(1)
    body_md = body_md.replace("## References\n\n" + refs_md + "\n\n", "@@REFS@@\n\n")
    body_md = body_md.replace("### A. Limitations", "@@APPENDIX@@\n\n## A. Limitations")
    for h in ("### B. ", "### C. ", "### D. ", "### E. ", "### F. "):
        body_md = body_md.replace(h, "## " + h[4:])

    # Replace tables (and their caption line) with placeholders.
    tables = []

    def grab(m):
        block, cap = m.group(1), m.group(2)
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in block.strip().split("\n")]
        rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
        cap = re.sub(r"^\*Table [A-Z]?\d+\. ", "*", cap.strip())
        tables.append((rows, cap))
        return f"@@TABLE{len(tables) - 1}@@\n"

    body_md = re.sub(r"((?:^\|.*\n)+)\n(\*Table .+\*)\n", grab, body_md, flags=re.M)
    assert len(tables) == 4, len(tables)

    fig_cap = re.search(r"\[Insert Figure 1 here: fig_cross_family\.png\]\n\n\*Figure 1\. (.+?)\*\n", body_md, re.S)
    body_md = body_md.replace(fig_cap.group(0), "@@FIGURE@@\n")

    body = pandoc(body_md)
    for i, (rows, cap) in enumerate(tables):
        body = body.replace(f"@@TABLE{i}@@", table(rows, cap, i))
    fig = "\n".join([
        r"\begin{figure}[!t]", r"\centering",
        r"\includegraphics[width=0.86\textwidth]{fig_cross_family.pdf}",
        r"\caption{" + pandoc(fig_cap.group(1)).strip() + "}", r"\label{fig:cross}", r"\end{figure}"])
    body = body.replace("@@FIGURE@@", fig)

    refs = []
    for ln in refs_md.strip().split("\n"):
        ref = re.sub(r"^\d+\. ", "", ln)
        refs.append(r"\item " + pandoc(ref).strip())
    body = body.replace("@@REFS@@", "\\section{References}\n\\begin{list}{}{\\leftmargin=1.5em\\itemindent=-1.5em\\itemsep=2pt\\parsep=0pt}\\small\n"
                        + "\n".join(refs) + "\n\\end{list}")
    body = body.replace("@@APPENDIX@@", r"\clearpage\appendix\section*{Appendix}")


    tex = (HERE / "preamble.tex").read_text()
    tex = tex.replace("@@TITLE@@", tex_escape(title))
    tex = tex.replace("@@ABSTRACT@@", pandoc(abstract).strip())
    tex = tex.replace("@@BODY@@", body)
    (HERE / "main.tex").write_text(tex)
    print("wrote main.tex")


if __name__ == "__main__":
    main()
