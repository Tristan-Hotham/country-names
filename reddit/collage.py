"""Reddit collage: the world in Chinese characters with their literal glosses, Germany's six families of names,
and the headline numbers. 2400 x 3000 px. Every number from data/results.json.
Run: python3 reddit/collage.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figlib import *
import matplotlib.patheffects as pe

S, W, R = load()
C = S["countries"]; LI = {l["c"]: i for i, l in enumerate(S["langs"])}; CI = {c["q"]: i for i, c in enumerate(C)}
BGC = "#F5EFE3"; INK = "#22191A"; SEALC = "#B5301B"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGC)

# ---- title -------------------------------------------------------------------------------------
fig.text(.04, .972, "What does the world call your country?", fontproperties=DISP, fontsize=37, color=INK, va="top")
fig.text(.04, .925, f"Every country's name in {R['meta']['languages']} languages, from Wikidata: {R['meta']['names']:,} names. Below, the world in Chinese,\n"
         "read character by character. Most of these names were chosen for their sound, so the English is what\nthe characters mean on their own, a playful gloss rather than the origin of the name.",
         family=SER, fontsize=14.5, color=INK, va="top", linespacing=1.3)

# ---- hero: Chinese map ---------------------------------------------------------------------------
kc = {"sound": "#E2D8C6", "sound and meaning": "#EDB59D", "short form": "#D2694C", "translation": SEALC, "own name": "#4B2A5C"}
ax = fig.add_axes([0.0, .5, 1.0, .33]); ax.set_facecolor(BGC)
world(ax, W, lambda i: kc.get((S["zh"].get(C[i]["q"]) or {}).get("k"), "#E9E3D8"), edge=BGC, lw=.4, sea="#E3E9EA")
sw = [pe.withStroke(linewidth=3, foreground="#ffffffd8")]
OFFS = {"Q145": (-30, 54), "Q142": (-22, 40), "Q236": (24, 33), "Q189": (-20, 73), "Q183": (12, 58)}
boxes = []
order = sorted(range(len(C)), key=lambda i: (0 if (S["zh"].get(C[i]["q"]) or {}).get("k") in ("short form", "translation") else 1, C[i]["r"], -C[i]["pop"]))
for i in order:
    c = C[i]; z = S["zh"].get(c["q"])
    if not z or not c["sov"] or c["q"] in ("Q148", "Q423", "Q884", "Q865", "Q17", "Q881"): continue
    pri = z["k"] in ("short form", "translation")
    if c["r"] > 3 and not pri: continue
    x, y = ee(c["lx"], c["ly"])
    if c["q"] in OFFS:
        x2, y2 = ee(*OFFS[c["q"]]); ax.plot([x, x2], [y, y2], color=INK, lw=.8); x, y = x2, y2
    gl = " ".join((p[2] or "").split(",")[0] for p in z["p"] if p[2])
    if len(gl) > 20: gl = gl[:19].rsplit(" ", 1)[0] + "..."
    bw = max(len(z["s"]) * .1, len(gl) * .032) / 2 + .01
    box = (x - bw, y - .07, x + bw, y + .12)
    if not pri and any(box[0] < o[2] and box[2] > o[0] and box[1] < o[3] and box[3] > o[1] for o in boxes): continue
    if box[0] < ee(-180, 0)[0] + .1 or box[2] > ee(180, 0)[0] - .1: continue
    boxes.append(box)
    ax.text(x, y + .012, z["s"], ha="center", va="bottom", fontsize=15 if pri else 12.5, family=CJK, color=INK, path_effects=sw, fontweight="bold")
    ax.text(x, y + .006, gl, ha="center", va="top", fontsize=11 if pri else 9.5, family=SER, style="italic", color=SEALC, path_effects=sw)
    if len(boxes) >= 34: break
# key under the map
lx = .05
for k, lab in [("sound", "sound only"), ("sound and meaning", "sound + meaning"), ("short form", "short form"), ("translation", "translation"), ("own name", "own name")]:
    n = R["chinese"]["kinds"][k]
    fig.patches.append(matplotlib.patches.Rectangle((lx, .497), .016, .011, transform=fig.transFigure, color=kc[k], figure=fig))
    t = f"{lab}: {n}"; fig.text(lx + .021, .5025, t, family=MONO, fontsize=11, color=INK, va="center"); lx += .021 + .0083 * len(t) + .025
fig.text(.05, .482, f"Chinese names of {R['chinese']['n']} sovereign states. 美国 \"beautiful country\" is short for 美利堅, an early sound transcription of \"America\";\n"
         "德国 \"virtue country\" for 德意志 \"Deutsch\". Only 冰岛 Iceland (\"ice island\") and 黑山 Montenegro (\"black mountain\") are true translations.",
         family=SER + CJK, fontsize=11.5, color=INK, va="top", linespacing=1.4)

# ---- big numbers --------------------------------------------------------------------------------
nums = [(f"{round(R['chinese']['sound_share'] * 100)}%", f"of Chinese country names are\npure sound ({R['chinese']['kinds']['sound']} of {R['chinese']['n']})"),
        (f"{round(R['alike']['median'] * 100)}%", "of languages call the typical\ncountry something like its\nown name"),
        (str(R["alike"]["under_quarter"]), "countries echoed by fewer than\na quarter of languages: Greece,\nFinland, Japan, Germany..."),
        ("6", f"families of names for Germany,\nin {R['germany']['total']} languages")]
for k, (big, small) in enumerate(nums):
    x = .05 + k * .235
    fig.text(x, .432, big, fontproperties=DISP, fontsize=40, color=SEALC if k != 1 else JADE, va="top")
    fig.text(x, .382, small, family=SER, fontsize=12.5, color=INK, va="top", linespacing=1.3)
fig.add_artist(matplotlib.lines.Line2D([.04, .96], [.443, .443], transform=fig.transFigure, color=INK, lw=1.2))
fig.add_artist(matplotlib.lines.Line2D([.04, .96], [.318, .318], transform=fig.transFigure, color=INK, lw=1.2))

# ---- Germany map ----------------------------------------------------------------------------------
fig.text(.04, .305, "WHAT THE WORLD CALLS GERMANY", family=MONO, fontsize=12, color=INK, va="top", fontweight="medium")
fams = S["fam"]["Q183"]["f"]; of = S["fam"]["Q183"]["of"]; tq = CI["Q183"]
def gcol(i):
    c = C[i]; li = LI.get(c["lang"])
    if li is None or not S["names"][c["lang"]][tq]: return "#E9E3D8"
    k = of[li]
    if k in " x": return "#CFC6B6"
    return "#CFC6B6" if fams[int(k)]["id"] == "other" else FAMC[int(k)]
ax2 = fig.add_axes([.02, .108, .58, .178]); ax2.set_facecolor(BGC)
world(ax2, W, gcol, edge=BGC, lw=.3, sea="#E3E9EA")
fig.text(.04, .1, "Each country coloured by the name its own main language uses for Germany.", family=SER, fontsize=10.5, color=INK, style="italic")

# ---- families panel ----------------------------------------------------------------------------
SHORT = {"diutisc": "'of the people'", "nemets": "'the mute ones'", "saxon": "the Saxons", "baltic": "origin unclear", "germania": "Latin Germania", "alemanni": "the Alamanni"}
ex = {"diutisc": "Deutschland, Tyskland, 德国 Déguó", "nemets": "Niemcy, Nemačka", "saxon": "Saksa (Finnish)", "baltic": "Vokietija (Lithuanian)",
      "germania": "Germany, Germania, Jerman", "alemanni": "Allemagne, Alemania, Almanya"}
y = .292
for k, f in enumerate(fams):
    if f["id"] == "other": continue
    fig.patches.append(matplotlib.patches.Rectangle((.625, y - .021), .022, .019, transform=fig.transFigure, color=FAMC[k], figure=fig))
    fig.text(.655, y, f"{f['label'].replace(' family', '')}  {f['n']}", family=SER + CJK, fontsize=14, color=INK, va="top", fontweight="semibold")
    fig.text(.655, y - .0175, SHORT[f["id"]] + ": " + ex[f["id"]], family=SER + CJK, fontsize=11, color=MUT, va="top", style="italic")
    y -= .032
fig.text(.625, y + .002, f"Languages using each family, of {R['germany']['total']}; other: {R['germany']['other']}.", family=MONO, fontsize=9.5, color=MUT, va="top")

# ---- footer --------------------------------------------------------------------------------------
fig.add_artist(matplotlib.lines.Line2D([.04, .96], [.082, .082], transform=fig.transFigure, color=INK, lw=.8))
fig.text(.04, .073, f"Data: Wikidata labels for the {R['meta']['places']} countries and territories of Natural Earth, retrieved {R['meta']['retrieved']} (CC0).\n"
         "Families and meanings: English Wikipedia, \"Names of Germany\", \"List of country-name etymologies\",\n"
         "\"Transcription into Chinese characters\" (CC BY-SA 4.0). Glosses: CC-CEDICT, MDBG (CC BY-SA 4.0).\n"
         "Map: Natural Earth (public domain), Equal Earth projection. Long glosses are cut. Derived data CC BY-SA 4.0.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib.  Interactive: tristan-hotham.github.io/country-names",
         family=MONO, fontsize=9, color=MUT, va="top", linespacing=1.3)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "what_the_world_calls_each_other.png")
fig.savefig(out, dpi=200, facecolor=BGC); print(out)
