import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
import statsmodels.formula.api as smf
plt.rcParams.update({'font.family': 'PingFang HK', 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#CFC9C2', 'axes.labelcolor': '#55525E', 'xtick.color': '#8A8794', 'ytick.color': '#8A8794'})
INK, INK2, INK3, BLUE, ORANGE, ACC, GRID = '#1D1B22', '#55525E', '#8A8794', '#2A78D6', '#EB6834', '#D9467A', '#ECE8E3'
ev = pd.read_csv('events_v2_one_row_per_event.csv', parse_dates=['start']); ch = pd.read_csv('wl_chapters_v2.csv', parse_dates=['start'])
LAUNCH = pd.Timestamp('2025-03-27')
m = ev[ev.type_cn == '马拉松'].copy()
fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
ax.grid(axis='y', color=GRID, lw=0.8); ax.set_axisbelow(True)
for after, col, lab in ((False, BLUE, '上线前'), (True, ORANGE, '上线后')):
    s = m[m.after == after]; f = smf.ols('np.log(mass) ~ t', s).fit()
    tt = np.linspace(s.t.min(), s.t.max(), 50); d = LAUNCH + pd.to_timedelta(tt * 30.4, unit='D')
    rate = np.expm1(f.params['t']) * 100
    ax.scatter(s.start, s.mass, s=30, color=col, edgecolor='white', lw=1, zorder=3, label=f'{lab}的马拉松（n={len(s)}）')
    ax.plot(d, np.exp(f.params['Intercept'] + f.params['t'] * tt), color=col, lw=2, alpha=0.9, label=f'{lab}趋势：每月 {rate:+.1f}%')
ax.axvline(LAUNCH, color=ACC, lw=1.4); ax.text(LAUNCH, ax.get_ylim()[1], ' 国服上线 2025-03-27', color=ACC, va='top', fontsize=9)
ax.set_ylabel('第 10 万名 · 每天分数（百万）', fontsize=9); ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.legend(frameon=False, fontsize=8.2, loc='upper center', ncol=2, bbox_to_anchor=(0.5, -0.12))
fig.tight_layout(); fig.savefig('fig1_mass_trend.png', facecolor='white'); plt.close(fig)

groups = [('马拉松\n约 8 天，团体主题', ev[ev.type_cn == '马拉松'].gap, BLUE),
          ('World Link 整场\n约 12 天', ev[ev.type_cn == 'World Link 整场'].gap, INK3),
          ('World Link 单章 · 3 天\n单角色主题', ch[ch.ch_days == 3].gap, ORANGE),
          ('World Link 单章 · 2 天\n单角色主题', ch[ch.ch_days == 2].gap, '#C24A1C')]
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
for i, (lab, vals, c) in enumerate(groups):
    y = len(groups) - 1 - i
    ax.scatter(vals, y + np.random.default_rng(i).uniform(-0.18, 0.18, len(vals)), s=14, color=c, alpha=0.45, edgecolor='none')
    ax.plot([vals.median()] * 2, [y - 0.3, y + 0.3], color=c, lw=3, solid_capstyle='round')
    ax.text(vals.median(), y + 0.34, f'中位数 {vals.median():.0f} 倍  (n={len(vals)})', color=INK, fontsize=8.3, ha='center')
ax.set_yticks(range(len(groups))); ax.set_yticklabels([g[0] for g in groups][::-1], fontsize=8.6, color=INK2)
ax.set_xlabel('头部集中度 = 第 1000 名分数 ÷ 第 10 万名分数', fontsize=9); ax.set_ylim(-0.6, len(groups) - 0.25)
fig.tight_layout(); fig.savefig('fig2_format_gap.png', facecolor='white'); plt.close(fig)
print('ok')
