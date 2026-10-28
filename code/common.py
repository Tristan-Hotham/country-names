"""Shared helpers: paths, text cleaning, romanisation and the sound-skeleton similarity used across the scripts."""
import gzip, json, os, re
from difflib import SequenceMatcher
from anyascii import anyascii

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(ROOT, "work")
SRC = "/home/claude/hist/_data16"
BUNDLE = os.path.join(SRC, "country_names_bundle.json.gz")
CEDICT = os.path.join(SRC, "cc-cedict-1.1.1.tgz")
KANJIDIC = os.path.join(SRC, "kanjidic2-json-0.1.0.tgz")
NE50 = "/home/claude/hist/_data3/ne/geojson/ne_50m_admin_0_countries.geojson"
os.makedirs(DATA, exist_ok=True); os.makedirs(WORK, exist_ok=True)


def load_bundle():
    return json.load(gzip.open(BUNDLE, "rt", encoding="utf-8"))


DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")


def nodash(s):
    """House style: no en or em dashes and no double hyphens in anything published."""
    if s is None: return s
    s = s.translate(DASHES)
    while "--" in s: s = s.replace("--", "-")
    return s


def wiki_clean(t):
    """Wikitext to plain text, good enough for short quoted passages."""
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    for _ in range(4):
        t = re.sub(r"\{\{(?:lang|Lang|wikt-lang|transliteration|Transliteration|transl|Transl)\|[^|{}]*\|([^|{}]*)(?:\|[^{}]*)?\}\}", r"\1", t)
        t = re.sub(r"\{\{(?:langx|lang-\w+)\|[^|{}]*\|([^|{}]*)(?:\|[^{}]*)?\}\}", r"\1", t)
        t = re.sub(r"\{\{nihongo\|([^|{}]*)\|([^|{}]*)(?:\|[^{}]*)?\}\}", r"\1 (\2)", t)
        t = re.sub(r"\{\{(?:zhi|zh)\|[^{}]*?(?:c|s|t)=([^|{}]*)[^{}]*\}\}", r"\1", t)
        t = re.sub(r"\{\{(?:IPA|IPAc-en|audio|respell)[^{}]*\}\}", "", t)
        t = re.sub(r"\{\{[^{}]*\}\}", "", t)
    t = re.sub(r"\[\[(?:File|Image):[^\]]*\]\]", "", t)
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", t)
    t = re.sub(r"'''''|'''|''", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = t.replace("&nbsp;", " ").replace("&ndash;", "-").replace("&mdash;", "-")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" ([,.;:)])", r"\1", t)
    return nodash(t.strip())


def first_sentences(t, n=300):
    """First sentence(s) up to about n characters, cut at a sentence end where possible."""
    if len(t) <= n: return t
    cut = [m.end() for m in re.finditer(r'[.!?]["”)]?(?=\s+[A-Z(\[])', t) if m.end() <= n]
    return t[:cut[-1]] if cut else t[:n].rsplit(" ", 1)[0] + "..."


# ---- romanisation and sound skeletons -------------------------------------------------------------
STOP = {'the', 'of', 'and', 'republic', 'kingdom', 'islands', 'island', 'state', 'states', 'democratic', 'federal',
        'people', 'peoples', 'united', 'la', 'le', 'les', 'el', 'al', 'de', 'del', 'des', 'da', 'do', 'di', 'du', 'van',
        'von', 'den', 'der', 'het', 'na', 'an', 'a', 'i', 'y', 'e', 'et', 'und', 'og', 'och', 'ja', 've',
        'guo', 'koku', 'guk', 'quoc', 'kuk', 'ilhas', 'islas', 'iles', 'isole', 'inseln', 'eilanden'}
CL = {}
for _k, _v in {'K': 'gkcqx', 'B': 'bpvfw', 'D': 'dt', 'S': 'sz', 'J': 'j', 'L': 'lr', 'M': 'm', 'N': 'n'}.items():
    for _c in _v: CL[_c] = _k


def roman(s):
    return nodash(anyascii(s or ""))


def tokens(s):
    r = re.sub(r"[^a-z ]", " ", roman(s).lower().replace("'", "").replace("`", ""))
    return [t for t in r.split() if t]


def cskel(t):
    """Consonant-class skeleton of one romanised word: similar consonants merged, vowels dropped."""
    for a, b in (('ph', 'f'), ('th', 't'), ('tsch', 's'), ('dzh', 'j'), ('sch', 's'), ('sh', 's'), ('ch', 's'), ('ts', 's'),
                 ('tz', 's'), ('dzh', 'j'), ('zh', 'j'), ('dj', 'j'), ('gy', 'j'), ('ng', 'n')):
        t = t.replace(a, b)
    s = ''.join(CL.get(c, '') for c in t)
    return re.sub(r'(.)\1+', r'\1', s)


GENERIC = re.compile(r"^(re?s?publi|repubblika|jumh|jamh|cumh|xelg|halk|khalk|kongeri|koninkrijk|reino|royaume|regno|rike|mamlak|mamlaka|federa|feder|bundes|estado|etat|stato|staat|savez|zvez|ujedin|unid|uni|larab|arab|komari|demokr|narodn|ludow|lidov|popul|people|volks|folk|sosiali|sotsiali|islam|kingdom|union|commonwealth|confeder|eidgenoss)")


# "country" or "land" words that scripts written without spaces glue onto the name (Thai prathet, Lao pathet,
# Shan moeng, Khmer prateh, Burmese naingngan, Tibetan yul is part of the name and kept)
GLUED = ("ประเทศ", "ປະເທດ", "မိူင်း", "ប្រទេស", "နိုင်ငံ")


def cands(s):
    s = s or ""
    for g in GLUED:
        if g in s and s.replace(g, "").strip(): s = s.replace(g, " ")
    ts = [t for t in tokens(s) if t not in STOP and len(t) > 1 and not GENERIC.match(t)] or tokens(s)
    out = []
    for t in ts:
        out.append(t)
        if t.startswith('al') and len(t) > 4: out.append(t[2:])          # Arabic article al-
        if t.startswith('l') and len(t) > 4 and t[1] not in 'aeiou': out.append(t[1:])
    return out


def sim1(a, b):
    ca, cb = cskel(a)[:3], cskel(b)[:3]
    if not ca or not cb or ca[0] != cb[0]: return 0.0
    if min(len(ca), len(cb)) == 1: return 1.0
    return SequenceMatcher(None, ca, cb).ratio()


def sim(a, b):
    """0 to 1: do two names start with the same run of consonant sounds? 0.6 or more counts as alike."""
    return max([sim1(x, y) for x in cands(a) for y in cands(b)] or [0.0])


ALIKE = 0.6


def script_of(s):
    import unicodedata
    for ch in s or "":
        if ch.isalpha():
            n = unicodedata.name(ch, "")
            for k in ("LATIN", "CYRILLIC", "GREEK", "ARABIC", "HEBREW", "DEVANAGARI", "BENGALI", "GURMUKHI", "GUJARATI",
                      "ORIYA", "TAMIL", "TELUGU", "KANNADA", "MALAYALAM", "SINHALA", "THAI", "LAO", "TIBETAN", "MYANMAR",
                      "GEORGIAN", "HANGUL", "ETHIOPIC", "CHEROKEE", "CANADIAN", "KHMER", "MONGOLIAN", "ARMENIAN",
                      "THAANA", "TIFINAGH", "NKO", "SYRIAC", "OL CHIKI", "JAVANESE", "BALINESE", "SUNDANESE",
                      "SYLOTI", "OGHAM", "RUNIC", "GOTHIC", "OLD ", "COPTIC", "VAI", "ADLAM", "LIMBU", "MEETEI",
                      "CHAKMA", "SAURASHTRA", "LEPCHA", "TAI ", "BUGINESE", "BATAK"):
                if n.startswith(k): return k.strip().title()
            if "CJK" in n: return "Han"
            if "HIRAGANA" in n or "KATAKANA" in n: return "Kana"
            return n.split(" ")[0].title()
    return "Other"
