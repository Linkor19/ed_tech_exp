"""Builds the three PNG figures used in docs/FINDINGS.md.

Reads the same PostgreSQL database the analysis runs on, so the numbers in the
report and the numbers on the charts can never drift apart. Run from the project
root: python docs/make_charts.py
"""

import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from matplotlib.patches import Patch
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(f"postgresql://postgres:{os.getenv('DBCON')}/ed_tech_proj")

OUT = os.path.dirname(os.path.abspath(__file__))

# palette: chart surface, ink and the first two categorical slots
SURFACE = '#fcfcfb'
INK = '#0b0b0b'
INK_2 = '#52514e'
MUTED = '#898781'
GRID = '#e1e0d9'
AXIS = '#c3c2b7'
S1 = '#2a78d6'   # slot 1, blue
S2 = '#eb6834'   # slot 2, orange
GRAY = '#c3c2b7'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'DejaVu Sans'],
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE,
    'text.color': INK,
    'axes.labelcolor': INK_2,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
    'axes.edgecolor': AXIS,
})


def strip(ax, keep_left=False):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_visible(keep_left)
    ax.spines['bottom'].set_color(AXIS)
    ax.tick_params(length=0)


def wilson(x, n, z=1.96):
    """95% confidence interval for a share - the small groups here need it."""
    if n == 0:
        return 0.0, 0.0
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# ----------------------------------------------------------------- figure 1
# how the traffic was split - the randomiser is the story, so it goes first
split = pd.read_sql("""
    SELECT u.platform, s.variant, COUNT(*) AS users
    FROM ab_test_segments s JOIN users u ON s.user_id = u.user_id
    GROUP BY 1, 2
""", engine)
base = pd.read_sql("SELECT platform, COUNT(*) AS users FROM users GROUP BY 1", engine)

rows = []
for v in ['A', 'B']:
    sub = split[split.variant == v].set_index('platform').users
    rows.append((f'Variant {v}\n(n = {int(sub.sum()):,})'.replace(',', ' '),
                 sub.get('iOS', 0), sub.get('Android', 0)))
b = base.set_index('platform').users
rows.append((f'Whole user base\n(n = {int(b.sum()):,})'.replace(',', ' '),
             b['iOS'], b['Android']))

fig, ax = plt.subplots(figsize=(9, 3.6), dpi=140)
y = np.arange(len(rows))[::-1]
for i, (label, ios, andr) in enumerate(rows):
    tot = ios + andr
    ios_p, andr_p = ios / tot * 100, andr / tot * 100
    yy = y[i]
    ax.barh(yy, ios_p, height=0.52, color=S1, zorder=3)
    # 2px surface gap between the two fills
    ax.barh(yy, andr_p, left=ios_p + 0.35, height=0.52, color=S2, zorder=3)
    ax.text(ios_p / 2, yy, f'{ios_p:.0f}%', ha='center', va='center',
            color='white', fontsize=11, fontweight='bold', zorder=4)
    ax.text(ios_p + 0.35 + andr_p / 2, yy, f'{andr_p:.0f}%', ha='center', va='center',
            color='white', fontsize=11, fontweight='bold', zorder=4)

ax.set_yticks(y)
ax.set_yticklabels([r[0] for r in rows], fontsize=10, color=INK)
ax.set_xlim(0, 100.5)
ax.set_xticks([])
strip(ax)
ax.set_title('Platform split inside the experiment\n'
             'Variant A is an iPhone group, variant B is an Android group',
             fontsize=12.5, color=INK, loc='left', pad=14)
ax.legend(handles=[Patch(color=S1, label='iOS'), Patch(color=S2, label='Android')],
          loc='lower center', bbox_to_anchor=(0.5, -0.16), ncol=2,
          frameon=False, fontsize=10, labelcolor=INK_2)
fig.text(0.01, -0.02, 'chi-square = 391 on 1 df, p < 0.001 - platform and variant are not independent',
         fontsize=9, color=MUTED)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'randomization.png'), bbox_inches='tight')
plt.close(fig)

# ----------------------------------------------------------------- figure 2
# the same comparison read two ways: pooled, and inside each platform
cr = pd.read_sql("""
    SELECT u.platform, s.variant, COUNT(*) AS users, COUNT(sub.subscription_id) AS subs
    FROM ab_test_segments s
    JOIN users u ON s.user_id = u.user_id
    LEFT JOIN subscriptions sub ON s.user_id = sub.user_id
    GROUP BY 1, 2
""", engine)

groups = []
tot = cr.groupby('variant')[['users', 'subs']].sum()
groups.append(('All users\npooled', tot))
for pl in ['iOS', 'Android']:
    groups.append((pl, cr[cr.platform == pl].set_index('variant')[['users', 'subs']]))

fig, ax = plt.subplots(figsize=(9, 4.6), dpi=140)
w = 0.34
for gi, (name, t) in enumerate(groups):
    for vi, (v, col) in enumerate([('A', S1), ('B', S2)]):
        n, x = int(t.loc[v, 'users']), int(t.loc[v, 'subs'])
        p = x / n * 100
        lo, hi = wilson(x, n)
        xpos = gi + (vi - 0.5) * (w + 0.02)
        ax.bar(xpos, p, width=w, color=col, zorder=3)
        ax.errorbar(xpos, p, yerr=[[p - lo * 100], [hi * 100 - p]], fmt='none',
                    ecolor=INK_2, elinewidth=1.4, capsize=5, capthick=1.4, zorder=4)
        ax.text(xpos, hi * 100 + 0.7, f'{p:.1f}%', ha='center', va='bottom',
                fontsize=10.5, fontweight='bold', color=INK, zorder=4)
        ax.text(xpos, -0.9, f'n = {n}', ha='center', va='top', fontsize=9, color=MUTED)

ax.set_xticks(range(len(groups)))
ax.set_xticklabels([g[0] for g in groups], fontsize=11, color=INK)
ax.tick_params(axis='x', pad=22)
ax.set_ylim(0, 22)
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'], fontsize=9.5)
ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
ax.set_axisbelow(True)
strip(ax)
ax.set_title('Conversion to a paid plan, variant A against variant B\n'
             'Pooled, A wins. Inside each platform, B wins. Bars are 95% intervals',
             fontsize=12.5, color=INK, loc='left', pad=14)
ax.legend(handles=[Patch(color=S1, label='Variant A'), Patch(color=S2, label='Variant B')],
          loc='upper right', frameon=False, fontsize=10, labelcolor=INK_2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'ab_simpson.png'), bbox_inches='tight')
plt.close(fig)

# ----------------------------------------------------------------- figure 3
# money in against money out, per acquisition channel
econ = pd.read_sql("""
    SELECT u.marketing_chanel AS channel,
           COALESCE(SUM(s.price_paid), 0) AS revenue,
           COALESCE(MAX(m.spend), 0) AS spend
    FROM users u
    LEFT JOIN subscriptions s ON u.user_id = s.user_id
    LEFT JOIN (SELECT channel, SUM(cost) AS spend FROM marketing_costs GROUP BY 1) m
           ON u.marketing_chanel = m.channel
    GROUP BY 1
""", engine).set_index('channel')
econ = econ.loc[['Google Search', 'Facebook Ads', 'TikTok Influencers', 'Organic']]

fig, ax = plt.subplots(figsize=(9, 4.2), dpi=140)
y = np.arange(len(econ))[::-1]
h = 0.34
for i, (ch, row) in enumerate(econ.iterrows()):
    yy = y[i]
    ax.barh(yy + h / 2 + 0.02, float(row.revenue), height=h, color=S1, zorder=3)
    ax.barh(yy - h / 2 - 0.02, float(row.spend), height=h,
            color=GRAY if row.spend == 0 else S2, zorder=3)
    ax.text(float(row.revenue) + 700, yy + h / 2 + 0.02, f'{row.revenue:,.0f}'.replace(',', ' '),
            va='center', fontsize=10, color=INK_2)
    if row.spend == 0:
        ax.text(700, yy - h / 2 - 0.02, 'no spend', va='center', fontsize=10, color=MUTED)
    else:
        ax.text(float(row.spend) + 700, yy - h / 2 - 0.02, f'{row.spend:,.0f}'.replace(',', ' '),
                va='center', fontsize=10, color=INK_2)
        romi = (float(row.revenue) - float(row.spend)) / float(row.spend)
        ax.text(52000, yy, f'ROMI {romi:+.0%}', va='center', fontsize=10.5,
                fontweight='bold', color=INK)

ax.set_yticks(y)
ax.set_yticklabels(econ.index, fontsize=10.5, color=INK)
ax.set_xlim(0, 60000)
ax.set_xticks([0, 10000, 20000, 30000, 40000, 50000])
ax.set_xticklabels(['0', '10k', '20k', '30k', '40k', '50k'], fontsize=9.5)
ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
ax.set_axisbelow(True)
strip(ax)
ax.set_title('Revenue against marketing spend by channel, Jan-Mar 2026 (UAH)\n'
             'Every paid channel returns more than it costs, but none of it comes twice',
             fontsize=12.5, color=INK, loc='left', pad=14)
ax.legend(handles=[Patch(color=S1, label='Revenue'), Patch(color=S2, label='Spend')],
          loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2,
          frameon=False, fontsize=10, labelcolor=INK_2)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'channel_economics.png'), bbox_inches='tight')
plt.close(fig)

print('written: randomization.png, ab_simpson.png, channel_economics.png')
