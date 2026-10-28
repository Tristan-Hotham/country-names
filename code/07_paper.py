"""Step 7. The paper: fill code/paper_template.tex from data/results.json, add the tables, compile with xelatex.
Writes release/paper/ (tex and figures) and release/Hotham_What_the_World_Calls_Each_Other.pdf.
Run after 06_figures.py: python3 code/07_paper.py
"""
import json, os, re, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
S = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
PAPER = os.path.join(ROOT, "release", "paper"); PDF = os.path.join(ROOT, "release", "Hotham_What_the_World_Calls_Each_Other.pdf")


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}\\%"
    if f == "pct1": return f"{v * 100:.1f}\\%"
    if f == "f1": return f"{v:.1f}"
    if f == "len": return str(len(v))
    raise ValueError(f)


def tex(s):
    s = s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
    # wrap runs of CJK characters in the CJK font
    s = re.sub(r"([\u0400-\u052F]+)", r"\\un{\1}", s)
    return re.sub(r"([\u2E80-\u9FFF\u3040-\u30FF\uAC00-\uD7AF\uF900-\uFAFF]+)", r"\\zh{\1}", s)


def tables():
    g = R["families"]["Q183"]["families"]
    tg = "\n".join(f"{tex(f['label'])} & {tex(f['origin'])} & {f['n']} \\\\" for f in g)
    rows = []
    cq = {c["q"]: c for c in S["countries"]}
    for c in sorted(S["countries"], key=lambda c: -c["pop"]):
        z = S["zh"].get(c["q"])
        if c["sov"] and z and z["k"] in ("short form", "translation"):
            chars = "; ".join(f"{ch} {gl.split(',')[0]}" for ch, role, gl in z["p"])
            rows.append(f"{tex(c['n'])} & {tex(z['s'])} {tex(z['py'])} & Chinese, {tex(z['k'])} & {tex(chars)} \\\\")
    for c in sorted(S["countries"], key=lambda c: -c["pop"]):
        j = S["ja"].get(c["q"])
        if j and j["a"]:
            chars = "; ".join(f"{ch} {j['g'][ch].split(',')[0]}" for ch in "".join(j["a"]) if ch in j["g"])
            rows.append(f"{tex(c['n'])} & {tex(', '.join(j['a']))} & Japanese, short form & {tex(chars)} \\\\")
    return tg, "\n".join(rows)


if __name__ == "__main__":
    os.makedirs(PAPER, exist_ok=True)
    t = open(os.path.join(HERE, "paper_template.tex"), encoding="utf-8").read()
    t = re.sub(r"\{\{([\w. ]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3)), t)
    tg, tc = tables()
    t = t.replace("/*TAB_GERMANY*/", tg).replace("/*TAB_CHINESE*/", tc)
    assert not re.search(r"\{\{[\w. ]+(\|\w+)?\}\}", t) and "—" not in t and "–" not in t and "--" not in t.replace("<!--", "")
    open(os.path.join(PAPER, "paper.tex"), "w", encoding="utf-8").write(t)
    with tempfile.TemporaryDirectory() as d:
        shutil.copy(os.path.join(PAPER, "paper.tex"), d)
        for f in os.listdir(PAPER):
            if f.endswith(".png"): shutil.copy(os.path.join(PAPER, f), d)
        for _ in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "paper.tex"], cwd=d, capture_output=True, text=True)
        if not os.path.exists(os.path.join(d, "paper.pdf")):
            print(r.stdout[-3000:]); raise SystemExit("xelatex failed")
        warn = [l for l in r.stdout.splitlines() if "Missing character" in l or "Overfull" in l]
        print("\n".join(warn[:20]))
        shutil.copy(os.path.join(d, "paper.pdf"), PDF)
    print("paper", os.path.getsize(PDF) // 1024, "KB")
