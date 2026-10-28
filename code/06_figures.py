"""Step 6. Static figures: header.png (1200 x 630 social card), the blog figures (release/blog/b_*.png, 1520 px wide)
and the paper figures (release/paper/fig_*.png, white background). All numbers come from data/results.json and
data/site.json.
Run: python3 code/06_figures.py
"""
import os, re, math
from figlib import *
from anyascii import anyascii

S, W, R = load()
C = S["countries"]; LANGS = S["langs"]; LI = {l["c"]: i for i, l in enumerate(LANGS)}; CI = {c["q"]: i for i, c in enumerate(C)}
BLOG = os.path.join(ROOT, "release", "blog"); PAPER = os.path.join(ROOT, "release", "paper")
KINDS = {"description": "a description", "people": "a people", "place": "a place, river or city", "person": "a person",
         "saint": "a saint or Christ", "state": "an older state or dynasty", "uncertain": "uncertain", "other": "other"}


def fam_info(q):
    if q in S["fam"]: return True, S["fam"][q]["f"], S["fam"][q]["of"]
    g = S["groups"][q]; return False, [{"id": x["k"], "label": x["ex"] + " spellings", "n": x["n"]} for x in g["g"]], g["of"]


def rev_colour(q):
    hand, fams, of = fam_info(q); tq = CI[q]
    def col(i):
        c = C[i]; li = LI.get(c["lang"])
        if li is None or not S["names"][c["lang"]][tq]: return NONE
        k = of[li]
        if k == " ": return NONE
        if k == "x": return OTHER
        f = fams[int(k)]
        return OTHER if f["id"] == "other" else FAMC[int(k) % len(FAMC)]
    return col


# Readable romanisations for the Germany map (anyascii drops the vowels of Arabic-script names). Standard
# transliterations of the Wikidata labels: Arabic ألمانيا, Persian آلمان, Urdu/Punjabi/Pashto جرمنی, Hindi जर्मनी, Bengali জার্মানি.
TRANS = {"ألمانيا": "Almānyā", "آلمان": "Ālmān", "جرمنی": "Jarmanī", "जर्मनी": "Jarmanī", "জার্মানি": "Jārmāni", "ජර්මනිය": "Jarmaniya",
         "ጀርመን": "Jermen", "גרמניה": "Germanya",
         "جرمني": "Jarmanī", "ประเทศเยอรมนี": "Yoeramani", "អាល្លឺម៉ង់": "Alleumong", "ဂျာမနီနိုင်ငံ": "Jarmani"}


def latin(name):
    if name in TRANS: return TRANS[name]
    if all(ord(ch) < 0x0530 or 0x1E00 <= ord(ch) <= 0x1EFF or ch in " -'" for ch in name): return name   # Latin, Greek and Cyrillic draw fine
    """Label text for a static map: Latin and CJK as written, other scripts romanised (matplotlib cannot shape them)."""
    if all(ord(ch) < 0x0370 or 0x2E80 <= ord(ch) <= 0x9FFF or 0x3040 <= ord(ch) <= 0x30FF or 0xAC00 <= ord(ch) <= 0xD7AF or ch in " -'" for ch in name):
        return name
    return anyascii(name)


def germany_map(path, bg, w=7.6, labels=True):
    fig = plt.figure(figsize=(w, w * .52), facecolor=bg); ax = fig.add_axes([0, .1, 1, .9]); ax.set_facecolor(bg)
    world(ax, W, rev_colour("Q183"), edge=bg, lw=.3)
    tq = CI["Q183"]
    if labels:
        done = []
        for i in sorted(range(len(C)), key=lambda i: (C[i]["r"], -C[i]["pop"])):
            c = C[i]
            if c["r"] > 3 or c["lang"] not in LI: continue
            n = S["names"][c["lang"]][tq]
            if not n: continue
            x, y = ee(c["lx"], c["ly"]); t = latin(n)
            wd = lambda u: sum(2 if ord(ch) > 0x2E80 else 1 for ch in u)
            if any(abs(x - a) < .045 * (wd(t) + wd(b)) / 2 and abs(y - bb) < .09 for a, bb, b in done): continue
            done.append((x, y, t))
            ax.text(x, y, t, ha="center", va="center", fontsize=6.6, family=SER + CJK, color=FG, fontweight="semibold",
                    path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=1.6, foreground="#ffffffcc")])
    hand, fams, of = fam_info("Q183")
    lx = .02
    for k, f in enumerate(fams):
        if f["id"] == "other": continue
        fig.patches.append(matplotlib.patches.Rectangle((lx, .045), .018, .03, transform=fig.transFigure, color=FAMC[k], figure=fig))
        lab = f"{f['label'].replace(' family', '')} {f['n']}"
        fig.text(lx + .024, .06, lab, fontsize=8.6, family=MONO, color=FG, va="center")
        lx += .024 + .0105 * len(lab) + .02
    save(fig, path)


def zh_map(path, bg, w=7.6):
    kc = {"sound": "#D8D1C3", "sound and meaning": "#E7A98F", "short form": "#C96A4E", "translation": SEAL, "own name": "#4B2A5C"}
    fig = plt.figure(figsize=(w, w * .56), facecolor=bg); ax = fig.add_axes([0, .1, 1, .9]); ax.set_facecolor(bg)
    world(ax, W, lambda i: kc.get((S["zh"].get(C[i]["q"]) or {}).get("k"), NONE), edge=bg, lw=.3)
    import matplotlib.patheffects as pe
    done = []
    order = sorted(range(len(C)), key=lambda i: (0 if (S["zh"].get(C[i]["q"]) or {}).get("k") in ("short form", "translation") else 1, C[i]["r"], -C[i]["pop"]))
    for i in order:
        c = C[i]; z = S["zh"].get(c["q"])
        pri = z and z["k"] in ("short form", "translation")
        if not z or not c["sov"] or (c["r"] > 4 and not pri) or c["q"] in ("Q148", "Q423", "Q884", "Q865"): continue
        x, y = ee(c["lx"], c["ly"])
        OFFS = {"Q145": (-26, 53), "Q142": (-17, 41), "Q236": (22, 36), "Q189": (-20, 72)}   # move crowded European labels out to sea
        if c["q"] in OFFS:
            x2, y2 = ee(*OFFS[c["q"]]); ax.plot([x, x2], [y, y2 + .01], color=FG, lw=.5); x, y = x2, y2
        gl = " ".join((p[2] or "").split(",")[0] for p in z["p"] if p[2])
        if len(gl) > 24: gl = gl[:23].rsplit(" ", 1)[0] + "..."
        bw = max(len(z["s"]) * .085, len(gl) * .024) / 2 + .005
        box = (x - bw, y - .055, x + bw, y + .095)
        if not pri and any(box[0] < o[2] and box[2] > o[0] and box[1] < o[3] and box[3] > o[1] for o in done): continue
        if box[0] < ee(-180, 0)[0] + .05 or box[2] > ee(180, 0)[0] - .05: continue
        done.append(box)
        sw = [pe.withStroke(linewidth=1.8, foreground="#ffffffd0")]
        ax.text(x, y + .015, z["s"], ha="center", va="bottom", fontsize=8.5, family=CJK, color=FG, path_effects=sw, fontweight="bold")
        ax.text(x, y + .012, gl, ha="center", va="top", fontsize=5.6, family=SER, style="italic", color=SEAL, path_effects=sw)
        if len(done) >= 46: break
    lx = .02
    for k, lab in [("sound", "sound only"), ("sound and meaning", "sound and meaning"), ("short form", "short form"), ("translation", "translation"), ("own name", "own name")]:
        n = R["chinese"]["kinds"].get(k, 0)
        fig.patches.append(matplotlib.patches.Rectangle((lx, .045), .018, .03, transform=fig.transFigure, color=kc[k], figure=fig))
        t = f"{lab} {n}"; fig.text(lx + .024, .06, t, fontsize=8.4, family=MONO, color=FG, va="center"); lx += .024 + .0105 * len(t) + .015
    save(fig, path)


def fam_bars(path, bg, w=7.6):
    qs = list(R["families"]); n = len(qs)
    fig = plt.figure(figsize=(w, .36 * n + .6), facecolor=bg); ax = fig.add_axes([.17, .02, .8, .91]); ax.set_facecolor(bg)
    for r, q in enumerate(qs):
        F = R["families"][q]; x = 0
        for k, f in enumerate(F["families"]):
            v = f["n"] / F["total"]
            col = OTHER if f["id"] == "other" else FAMC[k % len(FAMC)]
            ax.barh(r, v, left=x, height=.72, color=col, edgecolor=bg, linewidth=.6)
            lab = f["label"].replace(" family", "")
            if v > .022 * len(lab) * .62 + .02: ax.text(x + .008, r, lab, va="center", fontsize=7.6, color="white", family=SER + CJK)
            x += v
    ax.set_yticks(range(n)); ax.set_yticklabels([R["families"][q]["country"].replace("People's Republic of China", "China") for q in qs], family=MONO, fontsize=9)
    ax.invert_yaxis(); ax.set_xlim(0, 1); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], family=MONO, fontsize=8, color=MUT)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0); ax.xaxis.tick_top()
    save(fig, path)


# readable forms of the own names whose automatic romanisation is poor (forms as given in the etymology entries or
# standard romanisations)
OWNR = {"Q917": "Druk Yul", "Q668": "Bharat", "Q79": "Misr", "Q810": "al-Urdun", "Q262": "al-Jazair", "Q826": "Dhivehi Raajje",
        "Q230": "Sakartvelo", "Q423": "Choson", "Q884": "Daehan Minguk", "Q148": "Zhongguo", "Q17": "Nihon", "Q41": "Ellada"}


def low_bars(path, bg, w=7.6):
    rows = R["alike"]["lowest"][:22]
    fig = plt.figure(figsize=(w, .27 * len(rows) + .6), facecolor=bg); ax = fig.add_axes([.27, .07, .66, .92]); ax.set_facecolor(bg)
    for r, x in enumerate(rows):
        ax.barh(r, max(.004, x["share"]), height=.68, color=SEAL if x["share"] < .25 else UNLIKE)
        ax.text(max(.004, x["share"]) + .01, r, f"{round(x['share'] * 100)}%", va="center", fontsize=8, family=MONO, color=MUT)
    labs = [x["name"].replace("People's Republic of China", "China").replace("Central African Republic", "Central African Rep.") + (f"  ({OWNR.get(x['qid'], latin(x['own']))})" if (x["qid"] in OWNR or len(x["own"]) <= 12) and x["own"] != x["name"] else "") for x in rows]
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(labs, family=SER + CJK, fontsize=8.6); ax.invert_yaxis()
    ax.set_xlim(0, 1); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], family=MONO, fontsize=8, color=MUT)
    ax.grid(axis="x", color=RULE, lw=.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    save(fig, path)


def ety_bars(path, bg, w=7.6):
    ks = list(R["etymology"]["kinds"].items())
    fig = plt.figure(figsize=(w, .42 * len(ks) + .3), facecolor=bg); ax = fig.add_axes([.3, .02, .64, .96]); ax.set_facecolor(bg)
    for r, (k, v) in enumerate(ks):
        ax.barh(r, v, height=.66, color=OTHER if k in ("uncertain", "other") else JADE)
        ax.text(v + .8, r, str(v), va="center", fontsize=9.5, family=MONO, color=FG)
        ex = ", ".join(R["etymology"]["examples"][k][:3]) if k not in ("other",) else ""
    ax.set_yticks(range(len(ks))); ax.set_yticklabels([KINDS[k] for k, _ in ks], family=SER, fontsize=10); ax.invert_yaxis()
    ax.set_xticks([])
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    save(fig, path)


def lang_dots(path, bg, w=7.6):
    big = R["lang_alike"]["big"]
    fig = plt.figure(figsize=(w, .3 * len(big) + .7), facecolor=bg); ax = fig.add_axes([.3, .1, .65, .88]); ax.set_facecolor(bg)
    for r, b in enumerate(big):
        ax.plot([.6, b["share"]], [r, r], color=RULE, lw=1, zorder=1)
        ax.scatter([b["share"]], [r], s=46, color=SEAL if b["code"].startswith("zh") else JADE, zorder=2)
        ax.text(b["share"] + .006, r, f"{round(b['share'] * 100)}%", va="center", fontsize=8, family=MONO, color=MUT)
    ax.axvline(R["lang_alike"]["median"], color=MUT, lw=.8, ls=(0, (3, 3)))
    ax.text(R["lang_alike"]["median"], -.9, "median of all core languages ", fontsize=8, family=MONO, color=MUT, va="center", ha="right")
    ax.set_yticks(range(len(big))); ax.set_yticklabels([b["name"] for b in big], family=SER, fontsize=9.5); ax.set_ylim(len(big) - .5, -1.4)
    ax.set_xlim(.6, .95); ax.set_xticks([.6, .7, .8, .9]); ax.set_xticklabels(["60%", "70%", "80%", "90%"], family=MONO, fontsize=8, color=MUT)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0)
    save(fig, path)


def header(path):
    fig = plt.figure(figsize=(6, 3.15), facecolor=BG)
    ax = fig.add_axes([.36, .02, .66, .96]); ax.set_facecolor(BG)
    world(ax, W, rev_colour("Q183"), edge=BG, lw=.2)
    fig.text(.04, .86, "What the world\ncalls each other", fontproperties=DISP, fontsize=25, color=FG, va="top", linespacing=.95)
    fig.text(.04, .48, f"{R['meta']['names']:,} country names in\n{R['meta']['languages']} languages, and what\nthey mean", family=SER, fontsize=10.5, color=FG, va="top", linespacing=1.3)
    for k, (t, c) in enumerate([("Deutschland", FAMC[0]), ("Niemcy", FAMC[1]), ("Saksa", FAMC[2]), ("Vokietija", FAMC[3]), ("Germany", FAMC[4]), ("Allemagne", FAMC[5])]):
        fig.text(.04 + (k % 3) * .105, .2 - (k // 3) * .06, t, family=SER, fontsize=7.6, color=c, fontweight="semibold")
    fig.text(.04, .05, "Dr Tristan Hotham · tristan-hotham.github.io/country-names", family=MONO, fontsize=5.6, color=MUT)
    fig.savefig(path, dpi=200, facecolor=BG); plt.close(fig)


if __name__ == "__main__":
    header(os.path.join(ROOT, "header.png"))
    for d, bg, pre in ((BLOG, BG, "b_"), (PAPER, "#FFFFFF", "fig_")):
        germany_map(os.path.join(d, pre + "germany_map.png"), bg)
        zh_map(os.path.join(d, pre + "chinese_map.png"), bg)
        fam_bars(os.path.join(d, pre + "families.png"), bg)
        low_bars(os.path.join(d, pre + "renamed.png"), bg)
        ety_bars(os.path.join(d, pre + "etymology.png"), bg)
        lang_dots(os.path.join(d, pre + "languages.png"), bg)
    print("figures done")
