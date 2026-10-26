import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "charts")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "Inter",
    "font.size": 8.5,
    "axes.edgecolor": "#d9dedb",
    "axes.linewidth": 0.6,
    "axes.labelcolor": "#515c56",
    "xtick.color": "#6f7a74",
    "ytick.color": "#515c56",
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "savefig.dpi": 220,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

INK = "#17201c"
INK2 = "#515c56"
MUTED = "#6f7a74"
GRID = "#e6eae7"
BLUE = "#2a78d6"      # correct / intended
ORANGE = "#eb6834"    # main misreading / wrong
RED = "#e34948"       # significantly lower
GRAY = "#b9c1bc"      # context
LBLUE = "#6da7ec"     # label: Driver to origin
DBLUE = "#1c5cab"     # label: Driver arrival

d = json.load(open(os.path.join(HERE, "..", "data", "counts.json")))
BOTH = {"V1": 45, "V2": 40, "V3": 12, "V4": 40, "V5": 36, "V6": 15, "V7": 43, "V8": 41, "V9": 30}
CI2 = {"V1": 0, "V2": 2, "V3": 2, "V4": 2, "V5": 4, "V6": 4, "V7": 4, "V8": 0, "V9": 0}
TXT = {"V1": "4 min until driver arrives", "V2": "Driver to origin: <9 min", "V3": "<9 min",
       "V4": "Driver arrival: <9 min", "V5": "Driver to origin: 3–5 min", "V6": "3–5 min",
       "V7": "Driver arrival: 3–5 min", "V8": "Driver to origin: 4 min", "V9": "4 min"}
ORDER = ["V7", "V1", "V2", "V4", "V8", "V5", "V9", "V6", "V3"]
TIER = {k: "top" for k in ["V7", "V1", "V2", "V4", "V8", "V5"]}
TIER.update({"V9": "mid", "V6": "low", "V3": "low"})


def pct(k, m):
    v = d[k]; n = v["N"]
    x = {"q1": v["q1"][2], "q2": v["q2"][CI2[k]], "both": BOTH[k]}[m]
    return 100 * x / n


def wilson(x, n, z=1.96):
    p = x / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return 100 * (c - h), 100 * (c + h)


def _y(fig, inches):
    return 1 - inches / fig.get_figheight()


def title(fig, t, sub=None, x=0.012):
    fig.text(x, _y(fig, 0.04), t, ha="left", va="top", fontsize=11, fontweight="semibold", color=INK)
    if sub:
        fig.text(x, _y(fig, 0.27), sub, ha="left", va="top", fontsize=7.6, color=MUTED)


def clean(ax, grid_axis="x"):
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#d9dedb")
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def legend_row(fig, items, y=None, x0=0.012):
    y = _y(fig, 0.52)
    r = fig.canvas.get_renderer()
    W = fig.get_figwidth() * fig.dpi
    sq = 0.075 / fig.get_figheight()
    x = x0
    for color, label in items:
        fig.patches.append(plt.Rectangle((x, y - sq / 2), 0.075 / fig.get_figwidth(), sq,
                                         transform=fig.transFigure, color=color, ec="none"))
        t = fig.text(x + 0.11 / fig.get_figwidth(), y, label, va="center", fontsize=7.6, color=INK2)
        x = x + 0.11 / fig.get_figwidth() + t.get_window_extent(r).width / W + 0.22 / fig.get_figwidth()


# 1. Ranking: both-correct per copy with CI
def ranking():
    fig, ax = plt.subplots(figsize=(6.4, 3.35))
    fig.subplots_adjust(left=0.30, right=0.97, top=0.76, bottom=0.10)
    rows = ORDER[::-1]
    cols = {"top": BLUE, "mid": GRAY, "low": RED}
    for i, k in enumerate(rows):
        n = d[k]["N"]; v = pct(k, "both"); lo, hi = wilson(BOTH[k], n)
        ax.barh(i, v, height=0.56, color=cols[TIER[k]], edgecolor="white", linewidth=0)
        ax.plot([lo, hi], [i, i], color="#3d4642", linewidth=0.8, solid_capstyle="butt")
        ax.plot([lo, lo], [i - 0.12, i + 0.12], color="#3d4642", linewidth=0.8)
        ax.plot([hi, hi], [i - 0.12, i + 0.12], color="#3d4642", linewidth=0.8)
        ax.text(hi + 0.35, i, f"{v:.1f}%", va="center", fontsize=8, color=INK,
                fontweight="semibold" if k == "V7" else "normal")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{k}  ·  {TXT[k]}" for k in rows], fontsize=8)
    ax.set_xlim(0, 18)
    ax.set_xticks([0, 5, 10, 15])
    ax.set_xticklabels(["0%", "5%", "10%", "15%"])
    clean(ax)
    title(fig, "Six labeled copies tie at the top", "Got both questions right · line = 95% confidence interval")
    legend_row(fig, [(BLUE, "Top tier (statistically tied)"), (GRAY, "Middle"),
                     (RED, "Significantly lower")], y=0.835, x0=0.012)
    save(fig, "c1_ranking.png")


# 2. Pooled Q1 meaning
def q1_pooled():
    labels = ["Arrival time at destination", "Trip duration", "Wait at origin after car is found",
              "Time to find a car", "Wait for car after tapping Request", "Discount amount",
              "Time / distance between me and origin", "Didn't notice"]
    N = sum(v["N"] for v in d.values())
    vals = [100 * sum(v["q1"][i] for v in d.values()) / N for i in range(8)]
    idx = sorted(range(8), key=lambda i: vals[i])
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    fig.subplots_adjust(left=0.36, right=0.95, top=1-0.55/3.0, bottom=0.10)
    for j, i in enumerate(idx):
        c = BLUE if i == 2 else ORANGE if i == 4 else GRAY
        ax.barh(j, vals[i], height=0.58, color=c)
        tag = "  correct meaning" if i == 2 else "  most common reading" if i == 4 else ""
        ax.text(vals[i] + 0.3, j, f"{vals[i]:.1f}%{tag}", va="center", fontsize=8,
                color=INK, fontweight="semibold" if i in (2, 4) else "normal")
    ax.set_yticks(range(8))
    ax.set_yticklabels([labels[i] for i in idx], fontsize=8)
    ax.set_xlim(0, 30); ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
    clean(ax)
    title(fig, "Most people read the ETA as the total wait", f"What the time meant · all 9 copies · N = {N:,}")
    save(fig, "c2_q1_pooled.png")


# 3. Dumbbell: correct vs total-wait per copy
def dumbbell():
    fig, ax = plt.subplots(figsize=(6.4, 3.35))
    fig.subplots_adjust(left=0.30, right=0.97, top=0.76, bottom=0.10)
    rows = ORDER[::-1]
    for i, k in enumerate(rows):
        n = d[k]["N"]; c = 100 * d[k]["q1"][2] / n; w = 100 * d[k]["q1"][4] / n
        ax.plot([c, w], [i, i], color="#cfd5d1", linewidth=1.6, zorder=1)
        ax.scatter([c], [i], s=34, color=BLUE, edgecolor="white", linewidth=1.2, zorder=3)
        ax.scatter([w], [i], s=34, color=ORANGE, edgecolor="white", linewidth=1.2, zorder=3)
        ax.text(c - 0.6, i, f"{c:.0f}%", ha="right", va="center", fontsize=7.4, color=INK2)
        ax.text(w + 0.6, i, f"{w:.0f}%", ha="left", va="center", fontsize=7.4, color=INK2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{k}  ·  {TXT[k]}" for k in rows], fontsize=8)
    ax.set_xlim(0, 30); ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
    clean(ax)
    title(fig, "The 'total wait' reading wins in every copy", "Share of respondents per copy")
    legend_row(fig, [(BLUE, "Correct: wait at origin after car is found"),
                     (ORANGE, "Wait for car after tapping Request")], y=0.835)
    save(fig, "c3_dumbbell.png")


# 4. Label groups
def label_groups():
    groups = {"No label": ["V3", "V6", "V9"], "Driver to origin": ["V2", "V5", "V8"],
              "Driver arrival": ["V4", "V7"]}
    cols = [GRAY, LBLUE, DBLUE]
    metrics = [("q1", "Understood the meaning"), ("q2", "Remembered the time"), ("both", "Both right")]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    fig.subplots_adjust(left=0.07, right=0.98, top=0.74, bottom=0.12)
    w = 0.24
    for gi, (g, ks) in enumerate(groups.items()):
        n = sum(d[k]["N"] for k in ks)
        for mi, (m, _) in enumerate(metrics):
            x = sum({"q1": d[k]["q1"][2], "q2": d[k]["q2"][CI2[k]], "both": BOTH[k]}[m] for k in ks)
            v = 100 * x / n
            xpos = mi + (gi - 1) * (w + 0.03)
            ax.bar(xpos, v, width=w, color=cols[gi], linewidth=0)
            ax.text(xpos, v + 0.8, f"{v:.1f}%", ha="center", va="bottom", fontsize=7.6, color=INK)
    ax.set_xticks(range(3)); ax.set_xticklabels([m[1] for m in metrics], fontsize=8.5, color=INK2)
    ax.set_ylim(0, 48); ax.set_yticks([0, 20, 40]); ax.set_yticklabels(["0%", "20%", "40%"])
    clean(ax, "y"); ax.spines["bottom"].set_visible(True)
    title(fig, "Adding a label lifts every measure", "Pooled by label · V1 not included (different wording)")
    legend_row(fig, [(GRAY, "No label (V3, V6, V9)"), (LBLUE, "Driver to origin (V2, V5, V8)"),
                     (DBLUE, "Driver arrival (V4, V7)")], y=0.84)
    save(fig, "c4_label_groups.png")


# 5. Heatmap label x format
def heatmap():
    rows = ["No label", "Driver to origin:", "Driver arrival:"]
    colsx = ["< 9 min", "3–5 min", "4 min"]
    grid = [["V3", "V6", "V9"], ["V2", "V5", "V8"], ["V4", "V7", "V1"]]
    cmap = LinearSegmentedColormap.from_list("b", ["#e6f0fc", "#9ec5f4", "#3987e5", "#1c5cab"])
    fig, ax = plt.subplots(figsize=(6.4, 2.75))
    fig.subplots_adjust(left=0.24, right=0.80, top=0.76, bottom=0.04)
    for r in range(3):
        for c in range(3):
            k = grid[r][c]; v = pct(k, "both")
            col = cmap(min(v / 12.5, 1))
            ax.add_patch(plt.Rectangle((c + 0.03, 2 - r + 0.04), 0.94, 0.92, color=col, ec="none"))
            tc = "white" if v > 8 else INK
            ax.text(c + 0.5, 2 - r + 0.56, f"{v:.1f}%", ha="center", va="center", fontsize=11,
                    fontweight="semibold", color=tc)
            sub = k + ("*" if k == "V1" else "")
            ax.text(c + 0.5, 2 - r + 0.27, sub, ha="center", va="center", fontsize=7.4, color=tc)
    ax.set_xlim(0, 3); ax.set_ylim(0, 3)
    ax.set_xticks([0.5, 1.5, 2.5]); ax.set_xticklabels(colsx, fontsize=8.5, color=INK2)
    ax.xaxis.tick_top()
    ax.set_yticks([2.5, 1.5, 0.5]); ax.set_yticklabels(rows, fontsize=8.5, color=INK2)
    for s in ax.spines.values():
        s.set_visible(False)
    title(fig, "The label matters; the time format does not", "Got both questions right · by label (rows) and time format (columns)")
    fig.text(0.81, 0.40, "Format: no real\ndifference (p = .64)\n\nLabel vs none:\nclear difference\n(p < .001)",
             fontsize=7.4, color=INK2, va="center", linespacing=1.4)
    fig.text(0.24, -0.04, "* V1 reads “4 min until driver arrives”.", fontsize=7, color=MUTED)
    save(fig, "c5_heatmap.png")


# 6. Q2 stacked
def q2_stack():
    fig, ax = plt.subplots(figsize=(6.4, 3.35))
    fig.subplots_adjust(left=0.30, right=0.97, top=0.76, bottom=0.10)
    rows = ORDER[::-1]
    for i, k in enumerate(rows):
        v = d[k]; n = v["N"]
        c = 100 * v["q2"][CI2[k]] / n; dk = 100 * v["q2"][9] / n; wr = 100 - c - dk
        left = 0
        for val, col, tc in [(c, BLUE, "white"), (wr, ORANGE, "white"), (dk, GRAY, INK)]:
            ax.barh(i, val - 0.35, left=left, height=0.58, color=col, linewidth=0)
            if val > 7:
                ax.text(left + (val - 0.35) / 2, i, f"{val:.0f}%", ha="center", va="center",
                        fontsize=7.4, color=tc)
            left += val
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{k}  ·  {TXT[k]}" for k in rows], fontsize=8)
    ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    clean(ax)
    title(fig, "About 3 in 10 could not recall the time", "What respondents remembered about the time shown")
    legend_row(fig, [(BLUE, "Correct time"), (ORANGE, "Wrong time"), (GRAY, "Don't remember")], y=0.835)
    save(fig, "c6_q2_stack.png")


# 7. Recall given understanding
def recall_link():
    fig, ax = plt.subplots(figsize=(6.4, 2.0))
    fig.subplots_adjust(left=0.30, right=0.95, top=1-0.6/2.0, bottom=0.16)
    vals = [("Did not understand the meaning", 32.7, GRAY, "n = 2,825"),
            ("Understood the meaning", 63.7, BLUE, "n = 474")]
    for i, (lab, v, col, n) in enumerate(vals):
        ax.barh(i, v, height=0.55, color=col)
        ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8.5, color=INK, fontweight="semibold")
        ax.text(v + 10.5, i, n, va="center", fontsize=7.4, color=MUTED)
    ax.set_yticks([0, 1]); ax.set_yticklabels([v[0] for v in vals], fontsize=8)
    ax.set_xlim(0, 85); ax.set_xticks([0, 25, 50, 75]); ax.set_xticklabels(["0%", "25%", "50%", "75%"])
    clean(ax)
    title(fig, "People who understood the ETA also remembered the time",
          "Remembered the correct time · all 9 copies", )
    save(fig, "c7_recall_link.png")


for f in [ranking, q1_pooled, dumbbell, label_groups, heatmap, q2_stack, recall_link]:
    f()
print(sorted(os.listdir(OUT)))
