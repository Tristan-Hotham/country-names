"""Step 3. Chinese, Japanese, Korean and Vietnamese names: sound, meaning and character glosses.

Chinese: every country's simplified-Chinese Wikidata label, with pinyin and a gloss for each character from CC-CEDICT
(MDBG, CC BY-SA 4.0). Each character is tagged 'sound' (chosen for its sound) or 'meaning' (translated), using a short,
explicit list of meaning elements (country, island, republic, north, south, new, saint and so on) and hand-checked
whole names (Iceland 冰岛 'ice island', Montenegro 黑山 'black mountain'). Glosses are what the character means on
its own: for sound characters that is a fun reading, not the origin of the name.
Japanese: Wikidata labels; katakana means sound only. Kanji forms and one-character abbreviations are taken from the
Wikipedia article "Japanese exonyms" (CC BY-SA 4.0); kanji glosses from KANJIDIC2 (EDRDG, CC BY-SA 4.0).
Korean and Vietnamese: a name counts as a Sino-Korean or Sino-Vietnamese reading when it equals the KANJIDIC2 readings
of the characters of the Chinese or Japanese name (for example Korean 독일 Dogil = 獨逸, Vietnamese Đức = 德).
Writes data/chinese_names.csv, data/japanese_names.csv and work/cjk.json.
Run: python3 code/03_cjk.py
"""
import csv, json, re, tarfile, unicodedata, collections
from common import *

P = json.load(open(os.path.join(WORK, "prep.json"), encoding="utf-8"))
countries = {c["qid"]: c for c in P["countries"]}
lab = collections.defaultdict(dict)
for r in P["names"]: lab[r["qid"]][r["lang"]] = r["name"]
B = load_bundle()

# ---------- dictionaries -----------------------------------------------------------------------------
t = tarfile.open(CEDICT)
s = t.extractfile("package/data/all.js").read().decode("utf-8")
CE = json.loads(s[s.index("{"):].rstrip().rstrip(";"))["all"]
by_s, by_t = collections.defaultdict(list), collections.defaultdict(list)
for e in CE:
    by_s[e[1]].append(e); by_t[e[0]].append(e)
k = tarfile.open(KANJIDIC)
KD = {x["literal"]: x for x in json.loads(k.extractfile("package/KANJIS.json").read().decode("utf-8"))}
del s

TONES = {"a": "āáǎà", "e": "ēéěè", "i": "īíǐì", "o": "ōóǒò", "u": "ūúǔù", "ü": "ǖǘǚǜ"}


def tone(syl):
    m = re.match(r"([a-zü:]+)([1-5])$", syl.lower().replace("u:", "ü"))
    if not m: return syl
    w, n = m.group(1), int(m.group(2))
    if n == 5: return w
    for v in ("a", "e", "ou"):
        if v in w:
            i = w.index(v); return w[:i] + TONES[w[i]][n - 1] + w[i + 1:]
    for i in range(len(w) - 1, -1, -1):
        if w[i] in TONES: return w[:i] + TONES[w[i]][n - 1] + w[i + 1:]
    return w


def pinyin(p):
    return "".join(tone(x) for x in p.split())


BAD = re.compile(r"surname|abbr\.|variant of|used in|old variant|see |Taiwan pr|CL:|\bclassifier\b|phonetic|transliteration|Germany|France|England|Britain|America|USA|Russia|Japan|Africa|Asia|Europe|Holland|India|Italy|Spain|Thailand|Korea|Vietnam|also pr|\(slang\)|\(loanword\)|\(literary\)|^\(bound form\) ?$", re.I)


def senses(e):
    d = e[3] if isinstance(e[3], list) else [e[3]]
    out = []
    for x in d:
        for y in x.split(";"):
            y = re.sub(r"\[[^\]]*\]|\([^)]*\)|\{[^}]*\}", "", y).strip(" ,")
            y = re.sub(r"\s+", " ", y)
            if y and not BAD.search(y) and len(y) <= 28 and y not in out: out.append(y)
    return out


def char_gloss(ch, py=None):
    ents = [e for e in by_s.get(ch, []) + by_t.get(ch, []) if len(e[1]) == 1 and e[2][:1].islower()]
    if py: ents.sort(key=lambda e: e[2].lower() != py.lower())
    for e in ents:
        g = senses(e)
        if g: return ", ".join(g[:2])
    return ""


def word_pinyin(w):
    for e in by_s.get(w, []) + by_t.get(w, []):
        if len(e[2].split()) == len(w): return e[2].split()
    out = []
    for ch in w:
        ents = [e for e in by_s.get(ch, []) + by_t.get(ch, []) if len(e[1]) == 1]
        ents.sort(key=lambda e: (not e[2][:1].islower(), -len(e[3]) if isinstance(e[3], list) else 0))
        out.append(ents[0][2] if ents else "?")
    return out


# ---------- Chinese ---------------------------------------------------------------------------------
SUFFIX = [("共和国", "republic"), ("合众国", "united states"), ("王国", "kingdom"), ("联邦", "federation"), ("群岛", "islands"),
          ("岛", "island"), ("国", "country")]
PREFIX = [("圣", "saint"), ("赤道", "equator"), ("美属", "US-held"), ("英属", "British-held"), ("法属", "French-held"),
          ("南", "south"), ("北", "north"), ("东", "east"), ("西", "west"), ("中", "central"), ("新", "new")]
PREFIX_OK = {"南非", "南苏丹", "北马其顿", "东帝汶", "中非", "中非共和国", "新西兰", "新喀里多尼亚", "赤道几内亚", "西撒哈拉",
             "北塞浦路斯", "北马里亚纳群岛", "美属萨摩亚", "美属维尔京群岛", "英属维尔京群岛", "英属印度洋领地", "法属波利尼西亚",
             "法属南部和南极领地", "南乔治亚和南桑威奇群岛"}
WHOLE = {  # names whose characters are all meaning; source given in the notes column
    "冰岛": ("translation", "Chinese exonyms: Iceland is a literal translation, 冰 ice and 岛 island"),
    "黑山": ("translation", "Chinese exonyms: Montenegro is translated, 黑 black and 山 mountain"),
    "中国": ("own name", "China's own name, Zhongguo, 'Middle Kingdom' (List of country-name etymologies)"),
    "日本": ("own name", "Japan's own name in characters, 日本 'sun origin' (List of country-name etymologies)"),
    "韩国": ("own name", "the Chinese reading of South Korea's own name 韓國 (Hanguk)"),
    "朝鲜": ("own name", "the Chinese reading of North Korea's own name 朝鮮 (Chosŏn)"),
    "大韩民国": ("own name", "the Chinese reading of South Korea's own name 大韓民國 (Daehan Minguk)"),
    "朝鲜民主主义人民共和国": ("own name", "the Chinese reading of North Korea's own name in characters"),
    "中华人民共和国": ("own name", "China's own official name in characters, People's Republic of China"),
    "中华民国": ("own name", "Taiwan's own official name in characters, 'Republic of China'"),
    "香港": ("own name", "the territory's own name, written in characters"),
    "澳门": ("own name", "the territory's own name, written in characters"),
    "越南": ("own name", "Vietnam's own name in characters, 'Viet South' (List of country-name etymologies)"),
}
ABBR = {  # X国 names: the first character abbreviates an older full transcription (checked in CC-CEDICT and Wikipedia)
    "德国": ("德意志", "Transcription into Chinese characters: 德 is abbreviated from 德意志 Déyìzhì, a transcription of Deutsch; literally 'moral country'"),
    "美国": ("美利坚", "Transcription into Chinese characters: abbreviated from 美利堅合眾國; 美利堅 an early transcription of America; literally 'beautiful country'"),
    "英国": ("英吉利", "Transcription into Chinese characters: 英 is abbreviated from 英吉利 Yīngjílì, the early transcription of English; literally 'hero country'"),
    "法国": ("法兰西", "CC-CEDICT: 法兰西 Fǎlánxī, France; 法 is its first character"),
    "泰国": ("", "泰 stands for Thai (CC-CEDICT: 'abbr. for Thailand')"),
}
zh_rows = []
for q, c in countries.items():
    nm = lab[q].get("zh-hans")
    if not nm: continue
    trad = lab[q].get("zh-hant", "")
    py = word_pinyin(nm)
    parts = []
    i, j = 0, len(nm)
    pre = suf = None
    if nm in PREFIX_OK or nm.startswith("圣"):
        for p, g in PREFIX:
            if nm.startswith(p): pre = (p, g); i = len(p); break
    for sfx, g in SUFFIX:
        if nm.endswith(sfx) and len(nm) > len(sfx) and not (sfx == "国" and nm[:-1] in ("中", "韩")):
            suf = (sfx, g); j = len(nm) - len(sfx); break
    if nm in WHOLE:
        kind, note = WHOLE[nm]
        parts = [(ch, "meaning", char_gloss(ch, py[n] if n < len(py) else None)) for n, ch in enumerate(nm)]
    else:
        kind = "sound"; note = ""
        if pre: parts.append((pre[0], "meaning", pre[1]))
        for n in range(i, j):
            parts.append((nm[n], "sound", char_gloss(nm[n], py[n] if n < len(py) else None)))
        if suf: parts.append((suf[0], "meaning", suf[1]))
        if pre or suf: kind = "sound and meaning"
        if nm in ABBR:
            kind = "short form"; note = ABBR[nm][1]
            parts[0] = (parts[0][0], "short for " + ABBR[nm][0] if ABBR[nm][0] else "short form", parts[0][2])
    zh_rows.append({"qid": q, "country": c["name"], "simplified": nm, "traditional": trad,
                    "pinyin": " ".join(pinyin(x) for x in py), "kind": kind, "note": nm and note,
                    "chars": [{"c": ch, "role": r, "gloss": g} for ch, r, g in parts]})

# ---------- Japanese --------------------------------------------------------------------------------
def is_kana(s):
    return all(unicodedata.name(ch, "").startswith(("KATAKANA", "HIRAGANA")) or ch in "ー・ =" for ch in s)


ja_art = B["wikipedia"]["Japanese exonyms"]["text"]
ja_extra = {}   # English article name -> {ateji:[], abbr:[]}
for row in ja_art.split("\n|-"):
    m = re.search(r"\n\|\s*(?:rowspan=\"\d\"\s*\|)?\s*\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", row)
    if not m: continue
    name = (m.group(2) or m.group(1)).strip()
    cells = re.findall(r"\{\{[Ll]ang\|ja\|([^}|]+)\}\}", row)
    abbr = re.findall(r"(?:Abbreviated|Also)\s*\{\{[Ll]ang\|ja\|([^}|]+)\}\}", row)
    e = ja_extra.setdefault(name, {"forms": [], "abbr": []})   # a country can appear in several tables: merge
    for f in cells:
        if len(f) > 1 and f not in e["forms"]: e["forms"].append(f)
    for a in abbr:
        if a not in e["abbr"]: e["abbr"].append(a)
JA_ABBR_TEXT = {  # stated in Wikipedia articles in the bundle, quoted in the notes
    "Q30": ("米国", "Ateji: 米国 Beikoku 'literally translates to \"rice country\"', from 亜米利加 Amerika"),
    "Q183": ("独", "Names of Germany: 独 is still used as an abbreviation, from 獨逸 Doitsu"),
}
ja_rows = []
for q, c in countries.items():
    nm = lab[q].get("ja")
    if not nm: continue
    kana = is_kana(nm)
    ex = ja_extra.get(c["enwiki"]) or ja_extra.get(c["name"]) or ja_extra.get(c["en"]) or {}
    forms = [f for f in ex.get("forms", []) if f != nm and not is_kana(f)]
    abbr = list(ex.get("abbr", []))
    note = ""
    if q in JA_ABBR_TEXT:
        a, note = JA_ABBR_TEXT[q]
        if a not in abbr: abbr.append(a)
    kanji = [ch for ch in nm + "".join(abbr) + "".join(forms[:1]) if ch in KD and not is_kana(ch)]
    gl = {}
    for ch in dict.fromkeys(kanji):
        ms = [m for m in KD[ch]["meanings"].get("en", []) if not BAD.search(m)]
        gl[ch] = ", ".join(ms[:2])
    ja_rows.append({"qid": q, "country": c["name"], "name": nm, "romaji": roman(nm) if kana else "", "script": "katakana (sound only)" if kana else "kanji or mixed",
                    "kanji_forms": [f for f in forms if not is_kana(f)][:3], "abbr": [a for a in abbr if not is_kana(a)][:3], "glosses": gl, "note": note})


# ---------- Korean and Vietnamese readings of the characters --------------------------------------------
VAR = {"德": "徳"}
KO_OK = {"미국", "영국", "태국", "대한민국", "조선민주주의인민공화국", "일본", "인도", "독일", "중화인민공화국", "중화민국"}


def readings(ch, key):
    x = KD.get(ch) or KD.get(VAR.get(ch, ""))
    return x["readings"].get(key, []) if x else []


def matches(word, target, key):
    """Can 'target' be spelled as one reading per character of 'word'?"""
    opts = [readings(ch, key) for ch in word]
    if not word or any(not o for o in opts): return False
    sep = " " if key == "vietnam" else ""
    tgt = target.lower().replace(" ", "") if key == "vietnam" else target.replace(" ", "")
    def go(i, rest):
        if i == len(opts): return rest == ""
        return any(rest.startswith(o.lower() if key == "vietnam" else o) and go(i + 1, rest[len(o):]) for o in opts[i])
    return go(0, tgt)


sino = []
for q, c in countries.items():
    cands = {lab[q].get("zh-hant", ""), lab[q].get("zh-hans", ""), lab[q].get("ja", "")}
    ex = ja_extra.get(c["enwiki"]) or ja_extra.get(c["name"]) or {}
    cands |= set(ex.get("forms", []))
    cands = {x for x in cands if x and not is_kana(x)}
    for lang, key in (("ko", "korean_h"), ("vi", "vietnam")):
        tgt = lab[q].get(lang)
        if not tgt: continue
        if lang == "ko" and tgt not in KO_OK: continue   # hangul that spells the sound is not a character reading
        tries = sorted(cands | {x[:1] for x in cands if x.endswith(("国", "國"))}, key=len)
        for w in tries:
            if matches(w, tgt, key):
                sino.append({"qid": q, "country": c["name"], "lang": lang, "name": tgt, "chars": w}); break

with open(os.path.join(DATA, "chinese_names.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["wikidata", "country", "simplified", "traditional", "pinyin", "kind", "characters_role_gloss", "note"])
    for r in zh_rows:
        w.writerow([r["qid"], r["country"], r["simplified"], r["traditional"], r["pinyin"], r["kind"],
                    " | ".join(f"{x['c']} {x['role']}: {x['gloss']}" for x in r["chars"]), r["note"]])
with open(os.path.join(DATA, "japanese_names.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["wikidata", "country", "japanese", "romanised_rough", "script", "kanji_forms", "abbreviations", "kanji_glosses", "note"])
    for r in ja_rows:
        w.writerow([r["qid"], r["country"], r["name"], r["romaji"], r["script"], " ".join(r["kanji_forms"]), " ".join(r["abbr"]),
                    " | ".join(f"{k} {v}" for k, v in r["glosses"].items()), r["note"]])
json.dump({"zh": zh_rows, "ja": ja_rows, "sino": sino}, open(os.path.join(WORK, "cjk.json"), "w", encoding="utf-8"), ensure_ascii=False)
sv = [r for r in zh_rows if countries[r["qid"]]["sovereign"]]
print("Chinese:", len(zh_rows), collections.Counter(r["kind"] for r in sv))
print("Japanese:", len(ja_rows), collections.Counter(r["script"] for r in ja_rows if countries[r["qid"]]["sovereign"]))
print("Sino readings:", collections.Counter(r["lang"] for r in sino), [(r["country"], r["name"], r["chars"]) for r in sino][:40])
