"""Step 5. Build index.html from code/page_template.html.

Every number in the text is a {{path|format}} token filled from data/results.json, so the page cannot drift from the
analysis. Facts that the text states in words are checked against the data first. The page fetches data/site.json
(names, meanings, glosses) and data/world.json (outlines) when it loads.
Run: python3 code/05_build_site.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
SITE = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "len": return str(len(v))
    raise ValueError(f)


def sub(m):
    return fmt(get(m.group(1)), m.group(3))


def check():
    """Facts the page, paper and blog state in words."""
    F = R["families"]
    ids = {q: [f["id"] for f in F[q]["families"]] for q in F}
    assert ids["Q28"][:3] == ["magyar", "ugry", "hungary"] and ids["Q55"][:4] == ["low", "holland", "belanda", "nederland"]
    assert ids["Q79"][:2] == ["misr", "egypt"] and ids["Q148"][:3] == ["zhongguo", "cathay", "china"]
    assert ids["Q41"][:3] == ["hellas", "yunan", "graeci"] and ids["Q17"][:2] == ["nihon", "japan"] and ids["Q38"][0] == "walh"
    g = R["germany"]
    assert g["germania"] > g["alemanni"] > g["diutisc"] > g["nemets"] > g["saxon"] > g["baltic"]
    assert R["germany_check"]["n"] - R["germany_check"]["ok"] == 10
    mis = {c for c, a, b in R["germany_check"]["mismatches"]}
    assert {"bg", "be"} <= mis
    low = [r["name"] for r in R["alike"]["lowest"]]
    under = low[:R["alike"]["under_quarter"]]
    for c in ["Armenia", "Albania", "Bhutan", "Greece", "Georgia", "Finland", "Croatia", "Montenegro", "Japan", "India", "Germany", "Hungary", "Egypt", "People's Republic of China"]:
        assert c in under, c
    for c in ["Jordan", "Czech Republic", "Central African Republic"]:
        assert c in low[:22] and c not in under, c
    big = R["lang_alike"]["big"]
    assert [b["code"] for b in big[:2]] == ["zh-hant", "zh-hans"] and big[15]["code"] == "id" and len(big) == 16
    assert R["iran"]["persia_n"] == 2 and {x[0] for x in R["iran"]["persia"]} == {"am", "ang"}
    ex = R["etymology"]["examples"]
    for k, cs in {"person": ["Colombia", "Bolivia", "Philippines", "Saudi Arabia"], "saint": ["El Salvador"], "uncertain": ["Peru", "Cuba", "Syria"]}.items():
        for c in cs: assert c in ex[k], (k, c)
    E = {c["n"]: c["e"] for c in SITE["countries"] if c.get("e")}
    for c, k in {"Costa Rica": "description", "Montenegro": "description", "Ecuador": "description", "Ukraine": "description",
                 "Poland": "people", "France": "people", "Finland": "people", "India": "place", "Zambia": "place", "Zimbabwe": "place"}.items():
        assert E[c]["kind"] == k, (c, E[c]["kind"])
    Z = {c["n"]: SITE["zh"].get(c["q"]) for c in SITE["countries"]}
    assert Z["Iceland"]["s"] == "冰岛" and Z["Iceland"]["k"] == "translation" and Z["Montenegro"]["s"] == "黑山"
    assert Z["Germany"]["s"] == "德国" and Z["United States"]["s"] == "美国" and Z["Germany"]["k"] == "short form"
    J = {c["n"]: SITE["ja"].get(c["q"]) for c in SITE["countries"]}
    assert J["Germany"]["n"] == "ドイツ" and J["United Kingdom"]["n"] == "イギリス" and "米国" in J["United States"]["a"]
    for c, a in {"Russia": "露国", "Australia": "豪州", "Philippines": "比島", "Iceland": "氷島", "Germany": "独"}.items():
        assert a in J[c]["a"], c
    S = {(r["country"], r["lang"]): (r["name"], r["chars"]) for r in R["sino"]["list"]}
    assert S[("United States", "ko")][0] == "미국" and S[("Germany", "ko")][0] == "독일" and S[("Netherlands", "vi")][0] == "Hà Lan"
    assert S[("Germany", "vi")] if ("Germany", "vi") in S else True


if __name__ == "__main__":
    check()
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", sub, tpl)
    slim = {k: R[k] for k in ("meta", "alike", "families", "etymology", "lang_alike")}
    slim["alike"] = {k: v for k, v in R["alike"].items()}
    html = html.replace("/*RESULTS*/", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
    assert "{{" not in html and "—" not in html and "–" not in html
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html) // 1024, "KB")
