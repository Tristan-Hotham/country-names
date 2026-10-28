"""Shared drawing helpers for the header, blog figures, paper figures and the Reddit collage: fonts, palette, the
Equal Earth projection and a world map drawn from data/world.json."""
import json, os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
FONTS = "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/"
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    if os.path.exists(FONTS + f): fm.fontManager.addfont(FONTS + f)
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"]:
    if os.path.exists(f): fm.fontManager.addfont(f)
DISP = fm.FontProperties(fname=FONTS + "FrauncesVar.ttf", weight=900) if os.path.exists(FONTS + "FrauncesVar.ttf") else fm.FontProperties(family="serif", weight="bold")
SER = ["Source Serif 4", "Noto Sans CJK SC", "DejaVu Serif"]
MONO = ["IBM Plex Mono", "Noto Sans CJK SC", "DejaVu Sans Mono"]
CJK = ["Noto Sans CJK SC"]
CJKB = ["Noto Serif CJK SC"]
plt.rcParams["font.family"] = SER

BG = "#F6F2EA"; FG = "#1F1C26"; MUT = "#655E66"; RULE = "#DCD4C4"; SEA = "#E2E8EA"
SEAL = "#B8361E"; JADE = "#2C7A6E"; GOLD = "#C08A1E"; NONE = "#E4DED3"; OTHER = "#BDB6A8"
ALIKE = "#A9D3C8"; UNLIKE = "#EBA58A"; HOME = "#E8C766"
FAMC = ["#B8361E", "#2C7A6E", "#C08A1E", "#4B6FB0", "#8E4E9E", "#5E8A2E", "#C2627F"]


def load():
    S = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
    W = json.load(open(os.path.join(ROOT, "data", "world.json"), encoding="utf-8"))
    R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
    return S, W, R


# Equal Earth projection (Savric, Patterson and Jenny 2018)
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2


def ee(lon, lat):
    t = math.asin(M * math.sin(math.radians(lat)))
    t2 = t * t; t6 = t2 * t2 * t2
    x = math.radians(lon) * math.cos(t) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = t * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


def rings(geom):
    if geom["type"] == "Polygon": return [geom["coordinates"][0]]
    return [p[0] for p in geom["coordinates"]]


def world(ax, W, colour_of, edge="#FFFFFF", lw=.35, skip_antarctica=True, sea=SEA):
    """Fill every country with colour_of(index); returns nothing. Antarctica (index of the 'AQ' outline) is skipped."""
    patches, cols = [], []
    for f in W["features"]:
        i = f["properties"]["i"]
        c = colour_of(i)
        if c is None: continue
        for r in rings(f["geometry"]):
            if skip_antarctica and max(p[1] for p in r) < -58: continue
            patches.append(Polygon([ee(*p) for p in r], closed=True)); cols.append(c)
    pc = PatchCollection(patches, facecolor=cols, edgecolor=edge, linewidth=lw)
    ax.add_collection(pc)
    # outline of the globe
    edge_pts = [ee(-180, la) for la in range(-60, 91, 2)] + [ee(180, la) for la in range(90, -61, -2)]
    ax.add_patch(Polygon(edge_pts, closed=True, facecolor=sea, edgecolor="none", zorder=-1))
    x0, _ = ee(-180, 0); x1, _ = ee(180, 0); _, y0 = ee(0, -58); _, y1 = ee(0, 84)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.axis("off")


def save(fig, path, dpi=200):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
