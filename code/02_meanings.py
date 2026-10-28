"""Step 2. What the names mean, as far as the sources say.

 a) English-name and own-name etymologies for every country, from Wikipedia's "List of country-name etymologies"
    (CC BY-SA 4.0), cleaned to plain text, with a rough type (people, person, feature, description, uncertain).
 b) Name families for 15 countries (code/families.py), each with a quote checked word for word against its source,
    and a check of the Germany families against the language lists in "Names of Germany".
Writes data/etymologies.csv, data/families.csv and work/meanings.json.
Run: python3 code/02_meanings.py
"""
import csv, json, re, collections
from common import *
from families import F

B = load_bundle()
W = B["wikipedia"]
P = json.load(open(os.path.join(WORK, "prep.json"), encoding="utf-8"))
countries = {c["qid"]: c for c in P["countries"]}
CLEAN = {k: re.sub(r"\s+", " ", wiki_clean(v["text"])) for k, v in W.items() if v.get("text")}


def has_quote(article, quote):
    q = re.sub(r"\s+", " ", nodash(quote))
    return q in CLEAN.get(article, "")


# ---------- a) etymologies ---------------------------------------------------------------------------
raw = W["List of country-name etymologies"]["text"]
parts = re.split(r"\n===\s*(.+?)\s*===\s*\n", raw)
by_title = {}
for h, body in zip(parts[1::2], parts[2::2]):
    m = re.match(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", h.strip())
    title = (m.group(1) if m else wiki_clean(h)).strip()
    by_title[title.replace("_", " ")] = body
ALIAS = {"Q884": "South Korea", "Q423": "Korea (North and South)", "Q1008": "Côte d'Ivoire", "Q574": "East Timor",
         "Q30": "United States", "Q148": "China", "Q865": "Taiwan", "Q145": "United Kingdom", "Q258": "South Africa",
         "Q1050": "Eswatini", "Q213": "Czech Republic", "Q221": "North Macedonia", "Q971": "Republic of the Congo",
         "Q974": "Democratic Republic of the Congo", "Q702": "Federated States of Micronesia", "Q1005": "The Gambia",
         "Q778": "The Bahamas", "Q55": "Netherlands", "Q17": "Japan", "Q836": "Burma", "Q1011": "Cabo Verde", "Q778": "Bahamas"}


def kind(t):
    s = t[:260].lower()
    if re.match(r"^(etymology|meaning|origin)( is)? (uncertain|unknown|unclear|disputed|obscure)", s) or s.startswith("uncertain"):
        return "uncertain"
    if re.search(r"named (after|for)|in hono(u)?r of|honou?ring|land of (bol|colum)|house of|after (king|queen|prince|emperor|sultan|sheikh|saint|st\.)", s):
        if not re.search(r"named (after|for) (the )?(river|lake|mountain|island|region|province|city|town|bay|gulf|sea|cape|tribe|people|former|earlier|ancient|kingdom|empire|state|colony|its |the [a-z]+ (river|lake|islands?|region|province|city|people|tribe))", s):
            return "person"
    if re.search(r"(land|country|home|realm|place) (of|for) the [a-z'À-ɏ -]*?(people|tribe|ians\b|ans\b|ese\b|s\b)|\bof the [a-z]+ (people|tribe)|\bethnonym|\bthe [a-z]+s\"", s):
        return "people"
    if re.search(r"\b(river|lake|mountain|island|islands|coast|sea|gulf|bay|cape|volcano|forest|plain|desert|equator|silver|ice|black|white|red|green|rich|swamp|marsh|valley|peak|rock|cliff)\b", s):
        return "feature"
    if re.search(r"self-descriptive|descriptive|south|north|east|west|central|new |united", s):
        return "description"
    return "other"


ety = {}
for q, c in countries.items():
    t = ALIAS.get(q) or c["enwiki"]
    body = by_title.get(t) or by_title.get(c["en"]) or by_title.get(c["name"])
    if not body: continue
    body = re.sub(r"<ref[^>]*/>", "", body)
    body = re.sub(r"<ref[^>]*>.*?</ref>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    lines = [re.sub(r"^(\{\{[^{}]*\}\}\s*)+", "", l) for l in body.split("\n")]
    lines = [l for l in lines if l.strip() and not re.match(r"^:?\s*In English, .{0,40} may be pronounced", l)]
    first = next((l for l in lines if re.match(r"^:(?!:)", l) or re.match(r"^[A-Za-z'\"]", l)), None)
    if not first: continue
    en = wiki_clean(re.sub(r"^:\*?\s*", "", first))
    own = []
    for l in lines:
        if l.startswith("::") or l.startswith(":*"):
            tx = wiki_clean(re.sub(r"^:+\*?\s*", "", l))
            if re.search(r"endonym|local name|native name|official name|its modern|the local", tx[:120], re.I):
                own.append(first_sentences(tx, 300))
    ety[q] = {"en": first_sentences(en, 340), "kind": kind(en), "own": own[:2], "article": "List of country-name etymologies"}

# hand corrections of the rough type, after reading every entry (see README)
KIND_FIX = json.load(open(os.path.join(HERE, "kind_fix.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "kind_fix.json")) else {}
for q, k in KIND_FIX.items():
    if q in ety: ety[q]["kind"] = k

# ---------- b) families ------------------------------------------------------------------------------
names = P["names"]
fam_of = {}
fam_rows = []
problems = []
for q, spec in F.items():
    for fid, label, origin, rx, quote in spec["fams"]:
        art = spec.get("source_override", {}).get(fid, spec["article"])
        if not has_quote(art, quote): problems.append((q, fid, art, quote[:60]))
    counts = collections.Counter()
    ex = collections.defaultdict(list)
    for r in names:
        if r["qid"] != q: continue
        rom = r["roman"].lower()
        f = "other"
        for fid, label, origin, rx, quote in spec["fams"]:
            if re.search(rx, rom):
                f = fid; break
        fam_of[(q, r["lang"])] = f
        if r["lang"] in P["core"] or True:
            counts[f] += 1
            if len(ex[f]) < 8: ex[f].append(r["name"])
    for fid, label, origin, rx, quote in spec["fams"] + [("other", "Other names", "other or unclear origins", "", "")]:
        fam_rows.append({"qid": q, "country": countries[q]["name"], "family": fid, "label": label, "origin": origin,
                         "n_languages": counts[fid], "examples": " / ".join(ex[fid]),
                         "source": spec.get("source_override", {}).get(fid, spec["article"]) if fid != "other" else "",
                         "quote": nodash(quote)})
if problems:
    for p in problems: print("QUOTE NOT FOUND:", p)
    raise SystemExit("fix quotes")

# Germany: check the families against the language lists in "Names of Germany"
gtext = W["Names of Germany"]["text"]
sec_map = {"diutisc": "From [[Old High German]]", "germania": "From the [[Latin]]", "alemanni": "From the name of the [[Alamanni]]",
           "saxon": "From the name of the [[Saxon people", "nemets": "From the [[Proto-Slavic]]", "baltic": None}
lname2code = {}
for code, l in P["langs"].items():
    lname2code[l["name"].split(" (")[0].lower()] = code
lname2code.update({"modern english": "en", "irish": "ga", "chinese": "zh-hans", "malay": "ms", "scottish gaelic": "gd",
                   "low german/low saxon": "nds", "norwegian": "nb", "modern hebrew": "he", "swahili": "sw", "filipino": "tl",
                   "punjabi": "pa", "kurdish": "ku", "upper sorbian": "hsb", "lower sorbian": "dsb", "rumantsch": "rm", "serbo-croatian": "sh"})
check = []
for fid, head in sec_map.items():
    if not head: continue
    i = gtext.find("===" + head)
    if i < 0: continue
    j = gtext.find("\n===", i + 5)
    for m in re.finditer(r"\n\*\s*(?:\[\[[^\]|]*\|)?([^\]:\n]+?)\]?\]?\s*:", gtext[i:j]):
        ln = wiki_clean(m.group(1)).strip().lower()
        code = lname2code.get(ln)
        if code and ("Q183", code) in fam_of:
            check.append((code, fid, fam_of[("Q183", code)]))
ok = sum(a == b for _, a, b in check)
print(f"Germany check: {ok} of {len(check)} languages in the article's lists get the article's family")
mis = [(c, a, b) for c, a, b in check if a != b]
if mis: print("  mismatches:", mis)

with open(os.path.join(DATA, "etymologies.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["wikidata", "country", "english_name_etymology", "rough_type", "own_name_notes", "source"])
    for q, e in ety.items():
        w.writerow([q, countries[q]["name"], e["en"], e["kind"], " || ".join(e["own"]), "Wikipedia, " + e["article"] + " (CC BY-SA 4.0)"])
with open(os.path.join(DATA, "families.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(fam_rows[0].keys())); w.writeheader(); w.writerows(fam_rows)
json.dump({"ety": ety, "fam_of": {f"{q}|{l}": f for (q, l), f in fam_of.items()}, "fam_rows": fam_rows,
           "germany_check": {"n": len(check), "ok": ok, "mismatches": mis}},
          open(os.path.join(WORK, "meanings.json"), "w", encoding="utf-8"), ensure_ascii=False)
kinds = collections.Counter(e["kind"] for q, e in ety.items() if countries[q]["sovereign"])
print(len(ety), "etymologies;", dict(kinds))
for q in F:
    rows = [r for r in fam_rows if r["qid"] == q]
    print(countries[q]["name"], [(r["family"], r["n_languages"]) for r in rows])
