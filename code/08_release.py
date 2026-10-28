"""Step 8. Blog post (release/blog/post.html and meta.json) and Zenodo files (release/zenodo/).
Run after 06_figures.py and 07_paper.py: python3 code/08_release.py
"""
import json, os, re, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
BLOG = os.path.join(ROOT, "release", "blog"); ZEN = os.path.join(ROOT, "release", "zenodo")
PDF = "Hotham_What_the_World_Calls_Each_Other.pdf"
TITLE = "What the World Calls Each Other: Country Names in 262 Languages, and What They Mean"


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None: return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    raise ValueError(f)


def fill(t):
    return re.sub(r"\{\{([\w. ]+)(\|(\w+))?\}\}", lambda m: fmt(get(m.group(1)), m.group(3)), t)


if __name__ == "__main__":
    assert str(R["meta"]["languages"]) in TITLE
    post = fill(open(os.path.join(HERE, "blog_template.html"), encoding="utf-8").read())
    for img in re.findall(r"\{\{IMG\|([^|]+)\|", post): assert os.path.exists(os.path.join(BLOG, img)), img
    open(os.path.join(BLOG, "post.html"), "w", encoding="utf-8").write(post)
    meta = {"title": "What the world calls each other",
            "slug": "country-names",
            "excerpt": f"I mapped {R['meta']['names']:,} country names in {R['meta']['languages']} languages. Most countries are called something like their own name almost everywhere, but Germany has six families of names, and Chinese 'virtue country' and 'beautiful country' are mostly sound.",
            "seo_description": f"A world map of what {R['meta']['languages']} languages call every country, and what the names mean: Germany, Cathay, Yunan and more.",
            "tags": ["country names", "languages", "etymology", "maps", "Chinese", "Wikidata", "data"],
            "header_alt": "Title card reading 'What the world calls each other' on pale paper beside a world map coloured by the family of each country's name for Germany: purple Germany forms, green Allemagne forms, red Deutsch forms in Scandinavia and East Asia, teal Niemcy in the Slavic countries. Text: 54,037 country names in 262 languages, and what they mean."}
    assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
    json.dump(meta, open(os.path.join(BLOG, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    os.makedirs(ZEN, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "release", PDF), ZEN)
    for f in ("countries.csv", "languages.csv", "names.csv", "families.csv", "etymologies.csv", "chinese_names.csv", "japanese_names.csv"):
        shutil.copy(os.path.join(ROOT, "data", f), ZEN)
    zp = os.path.join(ZEN, "country-names_code_and_data.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for d in ("code", "data"):
            for f in sorted(os.listdir(os.path.join(ROOT, d))):
                p = os.path.join(ROOT, d, f)
                if os.path.isfile(p): z.write(p, f"country-names/{d}/{f}")
        for f in ("README.md", "LICENSE"): z.write(os.path.join(ROOT, f), f"country-names/{f}")
    a = R["alike"]; g = R["germany"]; c = R["chinese"]
    abstract = [
        "Countries are known abroad by names that often differ from their own: Deutschland is Allemagne, Niemcy and Saksa, Suomi is Finland, Hellas is Yunan. I assemble the Wikidata labels of all "
        f"{R['meta']['places']} countries and territories on the Natural Earth world map in the {R['meta']['languages']} languages that name at least 100 of them, {R['meta']['names']:,} names in all, and ask how often the world echoes a country's own name, which countries and languages depart from it most, and what the names mean where published sources say so.",
        f"A simple test on the first consonant sounds of romanised names, which agrees with hand-built name families for {a['validation']['share'] * 100:.1f}% of {a['validation']['names']:,} checked names, finds that the typical sovereign state is called by a name like its own in {round(a['median'] * 100)}% of other languages, but {a['under_quarter']} states, among them Germany, Greece, Finland, Japan, Hungary and China, are echoed by fewer than a quarter. "
        f"For fourteen countries I sort every name into families documented in Wikipedia, with each family's source sentence checked word for word: Germany's {g['total']} names fall into six families, led by forms of Latin Germania ({g['germania']}) and of French Allemagne ({g['alemanni']}), with only {g['diutisc']} echoing Deutsch.",
        f"Among large languages, Chinese departs most from countries' own names; of {c['n']} Chinese names for sovereign states, {c['kinds']['sound']} are pure sound transcriptions, and only {c['kinds']['translation']} are translations. Of the {R['etymology']['n']} sovereign states with an entry in Wikipedia's list of country-name etymologies, {R['etymology']['kinds']['description']} are named with a description, {R['etymology']['kinds']['people']} after a people and {R['etymology']['kinds']['place']} after a place. An interactive map lets readers label the world in any of the languages, or see what every language calls a chosen country."]
    zmeta = {"title": TITLE,
             "description_html": "".join(f"<p>{p}</p>" for p in abstract) + "<p>Interactive version: https://tristan-hotham.github.io/country-names/. Data and code: https://github.com/Tristan-Hotham/country-names. Blog post: to follow.</p>",
             "keywords": ["toponymy", "exonyms", "endonyms", "country names", "Wikidata", "etymology", "Chinese characters", "Japanese", "multilingual data", "open data"],
             "licence": "cc-by-sa-4.0",
             "related": [
                 {"identifier": "https://github.com/Tristan-Hotham/country-names", "relation": "issupplementedby", "resource_type": "software"},
                 {"identifier": "https://tristan-hotham.github.io/country-names/", "relation": "issupplementedby", "resource_type": "other"},
                 {"identifier": "https://www.wikidata.org", "relation": "isderivedfrom", "resource_type": "dataset"},
                 {"identifier": "https://en.wikipedia.org/wiki/List_of_country-name_etymologies", "relation": "isderivedfrom", "resource_type": "other"},
                 {"identifier": "https://en.wikipedia.org/wiki/Names_of_Germany", "relation": "isderivedfrom", "resource_type": "other"},
                 {"identifier": "https://www.mdbg.net/chinese/dictionary?page=cc-cedict", "relation": "isderivedfrom", "resource_type": "dataset"},
                 {"identifier": "https://www.edrdg.org/wiki/index.php/KANJIDIC_Project", "relation": "isderivedfrom", "resource_type": "dataset"},
                 {"identifier": "https://www.naturalearthdata.com", "relation": "isderivedfrom", "resource_type": "dataset"}]}
    json.dump(zmeta, open(os.path.join(ZEN, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    words = len(re.sub(r"<[^>]+>|\{\{IMG[^}]*\}\}", " ", post).split())
    print("post words", words, "| zip", os.path.getsize(zp) // 1024, "KB")
