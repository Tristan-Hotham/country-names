# What the world calls each other

An interactive world map of country names. Pick any of 262 languages and every country is labelled with its name in that language, with what the name literally means where the sources say so; or pick a country and see what every language calls it, with the families of names colour-coded. Built from 54,037 Wikidata labels for the 242 countries and territories of the Natural Earth world map, Wikipedia's articles on country-name etymologies, and the CC-CEDICT and KANJIDIC2 dictionaries.

Interactive page: https://tristan-hotham.github.io/country-names/
Paper: https://doi.org/10.5281/zenodo.23739847
Blog post: https://blog.tristanhotham.com/2026/10/28/country-names/

## Headline results

- 54,037 names: 242 countries and territories (196 sovereign states) in 262 languages and 32 scripts, from Wikidata labels retrieved 28 October 2026.
- For the typical sovereign state, 97% of the other core languages use a name that sounds like the state's own name; 120 of 196 states are echoed by 95% or more.
- 17 states are echoed by fewer than a quarter of languages: Armenia and Albania (0%), Bhutan, the Maldives, Greece, Georgia, China, Finland, Croatia, Montenegro, Japan, India, North Korea, Germany, South Korea, Hungary and Egypt.
- Germany's 261 names fall into six families documented in Wikipedia: Germania 137, Allemagne 58, Deutsch 37, Niemcy 18, Saksa 5, Vokietija 3 (other 3).
- Chinese departs most from countries' own names among large languages (68% of simplified Chinese names sound like the own name, against a median of 86% for core languages). Of 196 Chinese names for sovereign states, 163 (83%) are pure sound transcriptions, 20 mix sound and meaning, 5 are short forms (德国, 美国, 英国, 法国, 泰国) and 2 are translations (冰岛 Iceland, 黑山 Montenegro).
- Japanese writes 168 of 196 sovereign states in katakana (sound only); kanji short forms such as 米国 survive for a few.
- Of 193 sovereign states in Wikipedia's list of country-name etymologies, 60 are named with a description, 47 after a people, 42 after a place, 11 after a person, 9 after a saint or Christ, 6 after an older state; 16 are uncertain.
- Only 2 of 256 Wikidata names for Iran still resemble "Persia".

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`). Loads `data/site.json` and `data/world.json`. |
| `header.png` | Social card, 1200 x 630. |
| `data/countries.csv` | One row per country or territory: Wikidata id, ISO codes, sovereign flag, main language, own name, share of core languages whose name sounds like the own name, number of distinct names. |
| `data/languages.csv` | The 262 languages: Wikimedia code, name, Wikidata id, speakers (Wikidata), places named, core flag, main script. |
| `data/names.csv` | All 54,037 names: country, language, name, rough romanisation, sound-alike score (0 to 1; 0.6 or more counts as alike). |
| `data/families.csv` | Name families for 14 countries, with origin, number of languages, examples, source article and the checked quotation. |
| `data/etymologies.csv` | English-name and own-name etymologies from Wikipedia's list, with my rough kind of origin. |
| `data/chinese_names.csv` | Chinese names with pinyin, kind (sound, sound and meaning, short form, translation, own name) and a gloss and role for every character. |
| `data/japanese_names.csv` | Japanese names, script, kanji forms and short forms from Wikipedia, and KANJIDIC2 meanings. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/world.json` | Page data: names, romanisations, meanings and glosses; simplified Natural Earth outlines. |
| `code/` | Scripts, run in order (below). `common.py` (helpers and the sound test), `families.py` (family definitions and quotes), `kind_fix.json` (hand corrections of kinds), `figlib.py`, templates. |
| `release/` | Paper PDF and sources, blog figures and post, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## How to rerun

Needs Python 3 with shapely, matplotlib, Pillow and anyascii, and xelatex for the paper. Input data (read in place): `country_names_bundle.json.gz` (Wikidata labels and claims, and Wikipedia article wikitext), `cc-cedict-1.1.1.tgz`, `kanjidic2-json-0.1.0.tgz`, and Natural Earth `ne_50m_admin_0_countries.geojson`; set the paths at the top of `code/common.py`.

```
python3 code/01_prepare.py     # countries, languages, names, sound test
python3 code/02_meanings.py    # etymologies and name families (checks every quote)
python3 code/03_cjk.py         # Chinese, Japanese, Korean and Vietnamese glosses
python3 code/04_analyse.py     # results.json, site.json, world.json
python3 code/05_build_site.py  # index.html (checks facts stated in words)
python3 code/06_figures.py     # header.png, blog and paper figures
python3 code/07_paper.py       # paper PDF
python3 code/08_release.py     # blog post and Zenodo files
python3 reddit/collage.py      # collage
```

Steps 1 to 3 write intermediate files to `work/` (not part of the release).

## Method in brief

- **Own name**: the label in the country's main official language plus its Wikidata native label (and Nippon/Nihon, Hanguk, Choson, Lao).
- **Sounds like**: names romanised with anyascii, generic words (republic, kingdom, islands) and glued "country" prefixes (Thai, Lao, Khmer, Shan, Burmese) removed, words reduced to consonant classes; alike if the first class matches and the first three agree with a similarity of 0.6 or more. Checked against the hand-built families: 95.8% agreement on 3,622 names (53 false matches, 98 misses).
- **Families**: for 14 countries, families and origins taken from Wikipedia with a quoted sentence checked word for word; names assigned by spelling rules on romanised forms. For Germany, 99 of the 109 languages listed in "Names of Germany" are put in the article's family.
- **Kinds of origin**: my reading of every entry in the list of country-name etymologies.
- **Chinese**: CC-CEDICT pinyin and glosses; each character tagged as sound or meaning from a short explicit list of meaning elements and hand-checked whole names. A gloss of a sound character is what the character means on its own, not the meaning of the name.

## Caveats

One label per language; volunteers' labels occasionally use older or official forms; "languages" are Wikimedia language editions, not populations; the reverse map uses one main language per country; romanisations are rough; the sound test is crude (use it for patterns, not single names); kinds of origin are my sorting of a Wikipedia list.

## Sources and licences

- Wikidata (CC0): labels, native labels, official languages, speaker numbers. Retrieved 28 October 2026.
- English Wikipedia (CC BY-SA 4.0): List of country-name etymologies; Names of Germany, China, Greece, the Netherlands, Finland, Japan, Wales, Iran, the United States; Japanese exonyms; Ateji; Chinese exonyms; Transcription into Chinese characters.
- CC-CEDICT, MDBG (CC BY-SA 4.0), via the cc-cedict 1.1.1 npm package.
- KANJIDIC2, Electronic Dictionary Research and Development Group (CC BY-SA 4.0), via the kanjidic2-json 0.1.0 package.
- Natural Earth admin 0 countries 1:50m (public domain). Map tiles on the page: Esri. Map library: Leaflet. Romanisation: anyascii (ISC).

Data files and page text: **CC BY-SA 4.0** (they include text from Wikipedia and glosses from CC-CEDICT and KANJIDIC2). Code: **MIT** (see LICENSE).

## Citation

Hotham, T. (2026) What the world calls each other: country names in 262 languages, and what they mean. Zenodo. https://doi.org/10.5281/zenodo.23739847

Dr Tristan Hotham, Independent researcher, ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
