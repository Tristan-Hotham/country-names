"""Step 4. Every number used anywhere (data/results.json) and the page data (data/site.json, data/world.json).
Run: python3 code/04_analyse.py
"""
import json, collections, statistics, re
from common import *
from families import F
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

P = json.load(open(os.path.join(WORK, "prep.json"), encoding="utf-8"))
M = json.load(open(os.path.join(WORK, "meanings.json"), encoding="utf-8"))
X = json.load(open(os.path.join(WORK, "cjk.json"), encoding="utf-8"))
C = P["countries"]; L = P["langs"]; core = set(P["core"])
qi = {c["qid"]: i for i, c in enumerate(C)}
cq = {c["qid"]: c for c in C}
lab = collections.defaultdict(dict); al = collections.defaultdict(dict)
for r in P["names"]:
    lab[r["qid"]][r["lang"]] = r["name"]; al[r["qid"]][r["lang"]] = r["alike"]
sov = [c for c in C if c["sovereign"]]
R = {}

# ---- coverage --------------------------------------------------------------------------------------
R["meta"] = {"places": len(C), "sovereign": len(sov), "languages": len(L), "core_languages": len(core), "names": len(P["names"]),
             "retrieved": "28 October 2026", "langs_all_places": sum(1 for l in L.values() if l["n"] == len(C)),
             "langs_100m": sum(1 for l in L.values() if (l["speakers"] or 0) >= 1e8),
             "langs_10m": sum(1 for l in L.values() if 1e7 <= (l["speakers"] or 0) < 1e8),
             "langs_no_speakers": sum(1 for l in L.values() if not l["speakers"]),
             "scripts": len({l["script"] for l in L.values()})}
same_en = [r for r in P["names"] if r["lang"] != "en" and r["name"] == lab[r["qid"]].get("en")]
R["meta"]["same_as_english"] = len(same_en)
R["meta"]["same_as_english_share"] = round(len(same_en) / (len(P["names"]) - len(C)), 4)
sc = collections.Counter(r["script"] for r in P["names"])
R["scripts"] = [{"script": k, "names": v} for k, v in sc.most_common(12)]

# ---- like the country's own name -------------------------------------------------------------------
rows = [{"qid": c["qid"], "name": c["name"], "own": c["own"][0], "share": c["alike_share"], "n": c["n_core"], "distinct": c["n_distinct"]}
        for c in sov if c["alike_share"] is not None]
rows.sort(key=lambda r: r["share"])
R["alike"] = {"threshold": ALIKE, "lowest": rows[:25], "highest_n": sum(1 for r in rows if r["share"] >= 0.95),
              "median": round(statistics.median(r["share"] for r in rows), 4), "n": len(rows),
              "under_half": sum(1 for r in rows if r["share"] < 0.5), "under_quarter": sum(1 for r in rows if r["share"] < 0.25)}
mostd = sorted(rows, key=lambda r: -r["distinct"])
R["distinct_top"] = mostd[:12]
# validation of the sound test against the hand-built families: own family vs alike
OWNFAM = {"Q183": "diutisc", "Q148": "zhongguo", "Q41": "hellas", "Q55": "nederland", "Q28": "magyar", "Q33": "suomi", "Q17": "nihon",
          "Q79": "misr", "Q230": "sakartvelo", "Q222": "shqip", "Q399": "hayastan", "Q159": "rus", "Q34": "svea", "Q38": "italia"}
agree = tot = 0; tp = fp = fn = 0
for key, f in M["fam_of"].items():
    q, l = key.split("|")
    if q not in OWNFAM or l not in al[q]: continue
    a = al[q][l] >= ALIKE; b = f == OWNFAM[q]
    tot += 1; agree += a == b; tp += a and b; fp += a and not b; fn += b and not a
R["alike"]["validation"] = {"names": tot, "agree": agree, "share": round(agree / tot, 4), "false_alike": fp, "missed_alike": fn}

# ---- families ----------------------------------------------------------------------------------------
fam = {}
for q, spec in F.items():
    rows_q = [r for r in M["fam_rows"] if r["qid"] == q]
    tot_q = sum(r["n_languages"] for r in rows_q)
    fam[q] = {"country": cq[q]["name"], "total": tot_q,
              "families": [{"id": r["family"], "label": r["label"], "origin": r["origin"], "n": r["n_languages"],
                            "share": round(r["n_languages"] / tot_q, 4), "source": r["source"], "quote": r["quote"],
                            "examples": r["examples"]} for r in rows_q]}
R["families"] = fam
R["germany_check"] = M["germany_check"]
g = {f["id"]: f for f in fam["Q183"]["families"]}
R["germany"] = {k: g[k]["n"] for k in g} | {"total": fam["Q183"]["total"], "n_families": sum(1 for k in g if k != "other")}
R["finland"] = {"finland": next(f["n"] for f in fam["Q33"]["families"] if f["id"] == "finland"), "suomi": next(f["n"] for f in fam["Q33"]["families"] if f["id"] == "suomi"), "total": fam["Q33"]["total"]}

# ---- etymology types ---------------------------------------------------------------------------------
ety = M["ety"]
kinds = collections.Counter(ety[c["qid"]]["kind"] for c in sov if c["qid"] in ety)
R["etymology"] = {"n": sum(kinds.values()), "kinds": dict(kinds.most_common()),
                  "examples": {k: [cq[q]["name"] for q in ety if cq[q]["sovereign"] and ety[q]["kind"] == k][:12] for k in kinds}}

# ---- Chinese, Japanese, Korean, Vietnamese -------------------------------------------------------------
zs = [r for r in X["zh"] if cq[r["qid"]]["sovereign"]]
zk = collections.Counter(r["kind"] for r in zs)
R["chinese"] = {"n": len(zs), "kinds": dict(zk), "sound_share": round(zk["sound"] / len(zs), 4),
                "chars": sum(len(r["simplified"]) for r in zs)}
js = [r for r in X["ja"] if cq[r["qid"]]["sovereign"]]
R["japanese"] = {"n": len(js), "katakana": sum(r["script"].startswith("katakana") for r in js),
                 "with_abbr": [r["country"] for r in X["ja"] if r["abbr"]]}
R["japanese"]["katakana_share"] = round(R["japanese"]["katakana"] / len(js), 4)
R["sino"] = {"ko": sum(r["lang"] == "ko" for r in X["sino"]), "vi": sum(r["lang"] == "vi" for r in X["sino"]),
             "list": X["sino"]}

# ---- per language: how often does a language use a name like the country's own? ------------------------
acc = collections.defaultdict(lambda: [0, 0])
for r in P["names"]:
    c = cq[r["qid"]]
    if not c["sovereign"]: continue
    mine = {m.split("-")[0] for m in set(c["official"]) | {c["lang"]}}
    if r["lang"].split("-")[0] in mine: continue
    acc[r["lang"]][0] += 1; acc[r["lang"]][1] += al[r["qid"]][r["lang"]] >= ALIKE
la = [{"code": k, "name": L[k]["name"], "n": v[0], "share": round(v[1] / v[0], 4), "speakers": L[k]["speakers"]} for k, v in acc.items() if k in core]
la.sort(key=lambda r: r["share"])
R["lang_alike"] = {"lowest": la[:12], "highest": la[-8:][::-1], "median": round(statistics.median(r["share"] for r in la), 4),
                   "big": [r for r in la if (r["speakers"] or 0) >= 1e8]}
# Iran: names still from Persia
ir = [r for r in P["names"] if r["qid"] == "Q794"]
R["iran"] = {"n": len(ir), "persia": [[r["lang"], r["name"]] for r in ir if re.search("pers|pars|fars", r["roman"].lower())]}
R["iran"]["persia_n"] = len(R["iran"]["persia"])

# ---- language table ----------------------------------------------------------------------------------
R["big_languages"] = [{"code": l["code"], "name": l["name"], "speakers": l["speakers"], "n": l["n"]}
                      for l in sorted(L.values(), key=lambda l: -(l["speakers"] or 0))[:20]]
json.dump(R, open(os.path.join(DATA, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- page data -------------------------------------------------------------------------------------------
langs = sorted(L.values(), key=lambda l: (-(l["speakers"] or 0), l["name"]))
codes = [l["code"] for l in langs]
names = {c: [lab[x["qid"]].get(c, "") for x in C] for c in codes}
alike = {c: "".join("" if not lab[x["qid"]].get(c) else ("1" if al[x["qid"]][c] >= ALIKE else "0") for x in C) for c in codes}
# automatic spelling groups for every country: first two consonant classes of the first word
groups = {}
for x in C:
    keys = {}
    for c in codes:
        n = lab[x["qid"]].get(c)
        if not n: continue
        cs = [cskel(t) for t in cands(n)]
        keys[c] = (cs[0][:2] if cs and cs[0] else "?")
    cnt = collections.Counter(keys.values())
    top = [k for k, v in cnt.most_common(7) if v >= 3][:6]
    ex = {k: collections.Counter(roman(lab[x["qid"]][c]).split(" ")[0].capitalize() for c in codes if keys.get(c) == k and script_of(lab[x["qid"]][c]) == "Latin").most_common(1) for k in top}
    groups[x["qid"]] = {"g": [{"k": k, "n": cnt[k], "ex": (ex[k][0][0] if ex[k] else next(roman(lab[x["qid"]][c]).split(" ")[0].capitalize() for c in codes if keys.get(c) == k))} for k in top],
                        "of": "".join(str(top.index(keys[c])) if keys.get(c) in top else ("x" if c in keys else " ") for c in codes)}
famsite = {}
for q, spec in F.items():
    ids = [f[0] for f in spec["fams"]] + ["other"]
    famsite[q] = {"f": [{"id": f["id"], "label": f["label"], "origin": f["origin"], "n": f["n"], "src": f["source"], "quote": f["quote"]} for f in fam[q]["families"]],
                  "of": "".join(str(ids.index(M["fam_of"][f"{q}|{c}"])) if f"{q}|{c}" in M["fam_of"] else " " for c in codes)}
zh = {r["qid"]: {"s": r["simplified"], "t": r["traditional"], "py": r["pinyin"], "k": r["kind"], "note": r["note"],
                 "p": [[x["c"], x["role"], x["gloss"]] for x in r["chars"]]} for r in X["zh"]}
ja = {r["qid"]: {"n": r["name"], "r": r["romaji"], "s": r["script"], "f": r["kanji_forms"], "a": r["abbr"], "g": r["glosses"], "note": r["note"]} for r in X["ja"]}
site = {
    "countries": [{"q": x["qid"], "n": x["name"], "iso": x["iso2"], "lx": x["label_x"], "ly": x["label_y"], "r": x["labelrank"],
                   "sov": int(x["sovereign"]), "pop": x["pop"], "lang": x["lang"], "off": x["official"], "own": x["own"][:2], "sh": x["alike_share"],
                   "e": ety.get(x["qid"])} for x in C],
    "langs": [{"c": l["code"], "n": l["name"], "sp": l["speakers"], "g": l["group"], "k": l["n"], "s": l["script"]} for l in langs],
    "names": names, "alike": alike,
    "rom": {c: [roman(v) if v and script_of(v) != "Latin" else "" for v in names[c]] for c in codes}, "groups": groups, "fam": famsite, "zh": zh, "ja": ja,
    "sino": [[r["qid"], r["lang"], r["name"], r["chars"]] for r in X["sino"]],
}
s = json.dumps(site, ensure_ascii=False, separators=(",", ":"))
for bad in ("—", "–"):
    assert bad not in s, bad
open(os.path.join(DATA, "site.json"), "w", encoding="utf-8").write(s)

# world outlines, simplified, in the same order as countries
NE = json.load(open(NE50, encoding="utf-8"))
feats = []
for f in NE["features"]:
    gq = shape(f["geometry"]).simplify(0.06, preserve_topology=True)
    def rnd(o):
        if isinstance(o, (list, tuple)):
            if o and isinstance(o[0], (int, float)): return [round(o[0], 2), round(o[1], 2)]
            return [rnd(v) for v in o]
        return o
    gm = mapping(gq)
    feats.append({"type": "Feature", "properties": {"i": qi[f["properties"]["WIKIDATAID"]]}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
open(os.path.join(DATA, "world.json"), "w", encoding="utf-8").write(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
print("results.json, site.json", len(s) // 1024, "KB, world.json", os.path.getsize(os.path.join(DATA, "world.json")) // 1024, "KB")
print(json.dumps({k: R[k] for k in ("meta", "alike", "germany", "finland", "etymology", "chinese", "japanese")}, ensure_ascii=False)[:3500])
