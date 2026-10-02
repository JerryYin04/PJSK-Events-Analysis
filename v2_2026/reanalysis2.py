"""PJSK 活动档线分析 v2：sekai.best 接口数据，第 120 期 ~ 最新已结束活动
一场活动一行（World Link 整场一行，章节单独分析），按活动类型分层；
马拉松做中断时间序列；World Link 章节比较 3 天 vs 2 天。
"""
import pandas as pd, numpy as np
from scipy import stats
import statsmodels.formula.api as smf

b = pd.read_csv('sekai_best_borders.csv', dtype={'chapter': str})
# 接口缺档线的几条（第 120–123 期、124 期前两章）用原表补；第 199 期两边都没有，剔除
_old = pd.read_csv('pjsk_events.csv', dtype={'chapter': str})
# 与原表差超过 5% 的（第 126 期、124 期第 3 章：sekai.best 快照不完整）也以原表为准
_m = b.merge(_old[['id', 'chapter', 'pt_lines_1000']], on=['id', 'chapter'], how='left')
_bad = ((_m.r1000 / _m.pt_lines_1000 - 1).abs() > 0.05).values
b.loc[_bad, 'r1000'] = np.nan
for i, r in b[b.r1000.isna()].iterrows():
    o = _old[(_old.id == r.id) & (_old.chapter.astype(str) == str(r.chapter))]
    if len(o): b.loc[i, ['r1000', 'r100000']] = [o.pt_lines_1000.iloc[0], o.pt_lines_100000.iloc[0]]; b.loc[i, 'filled_from_old'] = True
b['filled_from_old'] = b['filled_from_old'].astype('boolean').fillna(False) if 'filled_from_old' in b else False
print('用原表补的条数', int(b.filled_from_old.sum()), '仍缺', int(b.r1000.isna().sum()))
b['start'] = pd.to_datetime(b.start_ms, unit='ms') + pd.Timedelta(hours=9)   # JST
b['end'] = pd.to_datetime(b.end_ms, unit='ms') + pd.Timedelta(hours=9)
b['days'] = (b.end - b.start).dt.total_seconds() / 86400
b['top'] = b.r1000 / b.days / 1e6
b['mass'] = b.r100000 / b.days / 1e6
b['gap'] = b.r1000 / b.r100000
LAUNCH = pd.Timestamp('2025-03-27')
b['after'] = b.start >= LAUNCH
b['t'] = (b.start - LAUNCH).dt.days / 30.4
TYPE = {'marathon': '马拉松', 'cheerful_carnival': '对战嘉年华', 'world_bloom': 'World Link 整场', 'world_bloom_chapter': 'World Link 单章'}
b['type_cn'] = b.type.map(TYPE)
FINALE = {180, 218}
b = b[~b.id.isin(FINALE)].dropna(subset=['r1000', 'r100000'])
ev = b[b.chapter == '-'].copy(); ch = b[b.chapter != '-'].copy()
ch['ch_days'] = ch.days.round().astype(int)

print(f'活动 {len(ev)} 场：{ev.start.min().date()} ~ {ev.start.max().date()}')
print(pd.crosstab(ev.type_cn, ev.after.map({False: '上线前', True: '上线后'})))

# 核对旧表
try:
    old = pd.read_csv('pjsk_events.csv'); old = old[old.chapter == '-'][['id', 'pt_lines_1000', 'pt_lines_100000']]
    m = ev.merge(old, on='id')
    d1 = (m.r1000 / m.pt_lines_1000 - 1).abs(); d2 = (m.r100000 / m.pt_lines_100000 - 1).abs()
    print(f'\n核对旧表 {len(m)} 场：第1000名最大偏差 {d1.max()*100:.2f}%  第10万名最大偏差 {d2.max()*100:.2f}%')
except Exception as e: print('核对跳过', e)

def mwu(a, b_): return stats.mannwhitneyu(a, b_).pvalue if len(a) > 1 and len(b_) > 1 else np.nan
print('\n== 分层：国服上线前后（中位数）==')
for t in ['马拉松', 'World Link 整场']:
    s = ev[ev.type_cn == t]
    for col in ['mass', 'top', 'gap']:
        a, c = s[~s.after][col], s[s.after][col]
        print(f'{t:<12}{col:<5} {a.median():8.3f} → {c.median():8.3f} ({(c.median()/a.median()-1)*100:+4.0f}%) n={len(a)}/{len(c)} MWU p={mwu(a, c):.2g}')

print('\n== 中断时间序列（马拉松）==')
mar = ev[ev.type_cn == '马拉松'].copy(); mar['t_after'] = mar.t.clip(lower=0)
for col in ['mass', 'top', 'gap']:
    f = smf.ols(f'np.log({col}) ~ t + after + t_after', mar).fit(cov_type='HC3')
    lo, hi = f.conf_int().loc['after[T.True]']
    print(f'{col:<5} 上线前趋势 {np.expm1(f.params["t"])*100:+.1f}%/月 (p={f.pvalues["t"]:.2g}) | 上线跳升 {np.expm1(f.params["after[T.True]"])*100:+.0f}% '
          f'[{np.expm1(lo)*100:+.0f}%, {np.expm1(hi)*100:+.0f}%] p={f.pvalues["after[T.True]"]:.2g} | 上线后斜率变化 {np.expm1(f.params["t_after"])*100:+.1f}%/月 (p={f.pvalues["t_after"]:.2g})')
print('上线后马拉松单独的趋势：')
post = mar[mar.after]
for col in ['mass', 'top']:
    f = smf.ols(f'np.log({col}) ~ t', post).fit(cov_type='HC3')
    print(f'  {col:<5} {np.expm1(f.params["t"])*100:+.1f}%/月 (p={f.pvalues["t"]:.2g}, n={len(post)})')

print('\n== 活动形式：头部集中度（第1000名 ÷ 第10万名）==')
groups = [('马拉松', ev[ev.type_cn == '马拉松']), ('对战嘉年华', ev[ev.type_cn == '对战嘉年华']), ('World Link 整场', ev[ev.type_cn == 'World Link 整场']),
          ('World Link 单章 3 天', ch[ch.ch_days == 3]), ('World Link 单章 2 天', ch[ch.ch_days == 2])]
for n, s in groups:
    if len(s): print(f'{n:<18} 中位数 {s.gap.median():5.1f} 倍  n={len(s)}  天数中位数 {s.days.median():.1f}')
c3, c2 = ch[ch.ch_days == 3], ch[ch.ch_days == 2]
if len(c2) and len(c3):
    print(f'单章 3 天 vs 2 天 集中度 MWU p={mwu(c3.gap, c2.gap):.2g}；第10万名每天分数 {c3.mass.median():.3f} vs {c2.mass.median():.3f}；第1000名 {c3.top.median():.2f} vs {c2.top.median():.2f}')
    print(f'  3 天章节时间 {c3.start.min().date()}~{c3.start.max().date()}，2 天章节时间 {c2.start.min().date()}~{c2.start.max().date()}（注意：时长变化和时间先后重合）')

print('\n== 马拉松：领衔团体（去掉逐月趋势后的头部热度）==')
f = smf.ols('np.log(top) ~ t + after', mar).fit(); mar['top_res'] = np.exp(f.resid)
print(mar.groupby('unit').top_res.agg(['mean', 'count']).round(2).sort_values('mean', ascending=False))
ev.to_csv('events_v2_one_row_per_event.csv', index=False); ch.to_csv('wl_chapters_v2.csv', index=False)
