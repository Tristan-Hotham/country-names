"""Step 1. Countries, languages and every name, from the Wikidata bundle and Natural Earth.

Writes:
  data/countries.csv   one row per Natural Earth 1:50m country or territory (242)
  data/languages.csv   one row per language kept (a Wikimedia language code with names for 100+ of the 242)
  data/names.csv       one row per country and language: the Wikidata label, romanised, alike/unlike the country's own name
  work/prep.json       the same for the next steps
Run: python3 code/01_prepare.py
"""
import csv, json, re, collections
from common import *

B = load_bundle()
C, LQ = B["countries"], B["languages"]
NE = json.load(open(NE50, encoding="utf-8"))

# ---------- languages --------------------------------------------------------------------------------
code2q = {}
for q, l in LQ.items():
    for c in ((l.get("claims") or {}).get("P424") or []):
        if c: code2q.setdefault(c, q)
code2q["zh-hans"] = code2q["zh-hant"] = code2q["zh"]


def speakers(q):
    v = [float(x["amount"]) for x in ((LQ.get(q, {}).get("claims") or {}).get("P1098") or []) if x and x.get("amount")]
    return max(v) if v else None


ne_ids = [f["properties"]["WIKIDATAID"] for f in NE["features"]]
cnt = collections.Counter(l for q in ne_ids for l in C[q]["labels"])
NAMEFIX = {"zh-hans": "Chinese (simplified)", "zh-hant": "Chinese (traditional)", "yue": "Cantonese", "nan": "Southern Min (Hokkien)",
           "pnb": "Punjabi (Shahmukhi script)", "pa": "Punjabi (Gurmukhi script)", "nb": "Norwegian (Bokmål)", "nn": "Norwegian (Nynorsk)",
           "sh": "Serbo-Croatian", "bn": "Bengali", "ku": "Kurdish (Kurmanji)", "ckb": "Kurdish (Sorani)", "ms": "Malay", "ang": "Old English",
           "zh-classical": "Classical Chinese", "be-tarask": "Belarusian (Taraškievica)", "mn": "Mongolian", "el": "Greek", "fy": "West Frisian",
           "arz": "Egyptian Arabic", "ary": "Moroccan Arabic", "azb": "South Azerbaijani", "az": "Azerbaijani", "sr": "Serbian", "lzh": "Classical Chinese"}
SKIP = {"mul", "zh"}  # 'mul' is not a language; plain 'zh' mixes scripts (we keep the simplified and traditional versions)
langs = {}
for code, n in cnt.items():
    if n < 100 or code in SKIP: continue
    if "-" in code and code not in ("zh-hans", "zh-hant", "be-tarask"): continue
    q = code2q.get(code)
    name = NAMEFIX.get(code) or (LQ[q]["label"] if q else None)
    if not name: continue
    langs[code] = {"code": code, "name": nodash(name), "qid": q, "speakers": speakers(q) if q else None, "n": n}
# disambiguate repeated names
byname = collections.defaultdict(list)
for c, l in langs.items(): byname[l["name"]].append(c)
for nm, cs in byname.items():
    if len(cs) > 1:
        for c in cs: langs[c]["name"] = f"{nm} ({c})"


def sp_group(s):
    if s is None: return "unknown"
    return "100m" if s >= 1e8 else "10m" if s >= 1e7 else "1m" if s >= 1e6 else "small"


# ---------- countries --------------------------------------------------------------------------------
PRIMARY_FIX = {  # main language where Wikidata's first-listed official language is not the most used one, or has no code
    "Q843": "ur", "Q813": "ky", "Q928": "tl", "Q77": "es", "Q23792": "ar", "Q148": "zh-hans", "Q865": "zh-hant",
    "Q8646": "zh-hant", "Q14773": "zh-hant", "Q664": "en", "Q574": "tet", "Q9648": "en", "Q921": "ms", "Q4824275": "en",
    "Q333946": "ur", "Q51": "en", "Q35": "da", "Q223": "kl", "Q4628": "fo"}


def claims(c, p):
    return [x for x in ((c.get("claims") or {}).get(p) or []) if x]


countries = []
for f in NE["features"]:
    p = f["properties"]; q = p["WIKIDATAID"]; c = C[q]
    sov = any(x.get("id") == "Q3624078" for x in claims(c, "P31")) or q == "Q35"
    off = [code for code in ([((LQ.get(x["id"], {}).get("claims") or {}).get("P424") or [None])[0] for x in claims(c, "P37")]) if code and code in c["labels"]]
    prim = PRIMARY_FIX.get(q) or (off[0] if off else "en")
    if prim not in c["labels"]: prim = "en"
    own = [c["labels"][prim]["value"]]
    for x in claims(c, "P1705"):
        if x.get("language", "").split("-")[0] == prim.split("-")[0] and x.get("text") and x["text"] not in own: own.append(x["text"])
    if q == "Q17": own += ["Nippon", "Nihon"]          # 日本: read in Japanese, not by its Chinese reading
    if q in ("Q884",): own += ["Hanguk"]
    if q in ("Q423",): own += ["Choson"]
    if q == "Q819": own += ["Lao"]                     # ລາວ, the Lao name without its "country" prefix, romanised
    en = c["labels"]["en"]["value"]
    countries.append({
        "qid": q, "name": nodash(p["NAME_EN"] if q not in ("Q30",) else "United States"), "en": nodash(en),
        "iso2": p["ISO_A2_EH"] if p["ISO_A2_EH"] != "-99" else "", "iso3": p["ADM0_A3"], "sovereign": sov,
        "continent": p["CONTINENT"], "subregion": p["SUBREGION"], "pop": int(p["POP_EST"] or 0),
        "label_x": round(p["LABEL_X"], 3), "label_y": round(p["LABEL_Y"], 3), "labelrank": p["LABELRANK"],
        "min_label": p["MIN_LABEL"], "lang": prim, "official": off, "own": [nodash(o) for o in own],
        "enwiki": nodash((c.get("sitelinks") or {}).get("enwiki", "")) if isinstance(c.get("sitelinks"), dict) else "",
        "named_after": [x["id"] for x in claims(c, "P138")]})

# ---------- names ------------------------------------------------------------------------------------
names = []
for ct in countries:
    labs = C[ct["qid"]]["labels"]
    for code in langs:
        if code not in labs: continue
        v = nodash(labs[code]["value"]).strip()
        s = max(sim(v, o) for o in ct["own"])
        names.append({"qid": ct["qid"], "lang": code, "name": v, "roman": roman(v), "alike": round(s, 2),
                      "script": script_of(v)})

# share alike per country, over 'core' languages (names for 200+ of the 242 places), excluding the country's own languages
core = [c for c, l in langs.items() if l["n"] >= 200]
by_q = collections.defaultdict(dict)
for r in names: by_q[r["qid"]][r["lang"]] = r
for ct in countries:
    mine = set(ct["official"]) | {ct["lang"]}
    rs = [by_q[ct["qid"]][c] for c in core if c in by_q[ct["qid"]] and c not in mine and c.split("-")[0] not in {m.split("-")[0] for m in mine}]
    ct["n_core"] = len(rs)
    ct["alike_share"] = round(sum(r["alike"] >= ALIKE for r in rs) / len(rs), 4) if rs else None
    ct["n_distinct"] = len({r["name"] for r in rs})

for l in langs.values():
    l["group"] = sp_group(l["speakers"])
    l["core"] = l["code"] in core
    rs = [r for r in names if r["lang"] == l["code"]]
    l["script"] = collections.Counter(r["script"] for r in rs).most_common(1)[0][0] if rs else ""

with open(os.path.join(DATA, "countries.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["wikidata", "name", "iso2", "iso3", "sovereign", "continent", "main_language", "own_name", "core_languages", "share_alike_own_name", "distinct_names"])
    for c in countries:
        w.writerow([c["qid"], c["name"], c["iso2"], c["iso3"], int(c["sovereign"]), c["continent"], c["lang"], " | ".join(c["own"]), c["n_core"], c["alike_share"], c["n_distinct"]])
with open(os.path.join(DATA, "languages.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["code", "language", "wikidata", "speakers_wikidata_max", "places_named", "core", "main_script"])
    for l in sorted(langs.values(), key=lambda l: -(l["speakers"] or 0)):
        w.writerow([l["code"], l["name"], l["qid"] or "", int(l["speakers"]) if l["speakers"] else "", l["n"], int(l["core"]), l["script"]])
with open(os.path.join(DATA, "names.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["wikidata", "country", "language_code", "name", "romanised", "alike_own_name_score"])
    nm = {c["qid"]: c["name"] for c in countries}
    for r in names:
        w.writerow([r["qid"], nm[r["qid"]], r["lang"], r["name"], r["roman"], r["alike"]])
json.dump({"countries": countries, "langs": langs, "names": names, "core": core}, open(os.path.join(WORK, "prep.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(countries), "places;", len(langs), "languages;", len(core), "core;", len(names), "names")
