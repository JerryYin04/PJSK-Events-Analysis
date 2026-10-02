"""从 sekai.best 的公开接口抓日服活动最终档线（第 120 期起）。每秒最多 1 个请求。"""
import json, time, csv, sys, datetime as dt, urllib.request, urllib.parse
API = 'https://api.sekai.best'
UA = {'User-Agent': 'Mozilla/5.0 (student portfolio research; ~1 req/s)'}
RANKS = [1, 10, 100, 1000, 10000, 50000, 100000]
def get(path, **params):
    params['region'] = 'jp'
    url = f'{API}{path}?{urllib.parse.urlencode(params)}'
    for attempt in range(4):
        try:
            time.sleep(1.0)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.load(r)
        except Exception as e:
            print('retry', path, e, file=sys.stderr); time.sleep(5 * (attempt + 1))
    return None
def final_borders(path, **extra):
    last = get(path, limit=1, sort=json.dumps({'timestamp': 'desc'}), **extra)
    rows = (last or {}).get('data', {}).get('eventRankings', [])
    if not rows: return None, {}
    ts = rows[0]['timestamp']
    full = get(path, timestamp=ts, **extra)
    rk = {x['rank']: int(x['score']) for x in full['data']['eventRankings']}
    return ts, {f'r{k}': rk.get(k) for k in RANKS}
MASTER = 'https://raw.githubusercontent.com/Sekai-World/sekai-master-db-diff/main/'
for name, local in (('events.json', 'events.json'), ('worldBlooms.json', 'wb.json')):
    import os
    if not os.path.exists(local):
        urllib.request.urlretrieve(MASTER + name, local)
ev = json.load(open('events.json')); wb = json.load(open('wb.json'))
now = dt.datetime.now().timestamp() * 1000
out = []
for e in sorted(ev, key=lambda x: x['id']):
    if e['id'] < 120 or e['aggregateAt'] > now: continue
    ts, b = final_borders(f"/event/{e['id']}/rankings")
    out.append({'id': e['id'], 'chapter': '-', 'chara_id': '', 'type': e['eventType'], 'name': e['name'], 'unit': e.get('unit', ''),
                'start_ms': e['startAt'], 'end_ms': e['aggregateAt'], 'snapshot': ts, **b})
    print(e['id'], e['eventType'], b.get('r1000'), b.get('r100000'), flush=True)
    if e['eventType'] == 'world_bloom':
        for c in sorted([c for c in wb if c['eventId'] == e['id'] and c['worldBloomChapterType'] == 'game_character'], key=lambda c: c['chapterNo']):
            ts, b = final_borders(f"/event/{e['id']}/chapter_rankings", charaId=c['gameCharacterId'])
            out.append({'id': e['id'], 'chapter': c['chapterNo'], 'chara_id': c['gameCharacterId'], 'type': 'world_bloom_chapter', 'name': e['name'], 'unit': '',
                        'start_ms': c['chapterStartAt'], 'end_ms': c['aggregateAt'], 'snapshot': ts, **b})
            print('  ch', c['chapterNo'], b.get('r1000'), b.get('r100000'), flush=True)
with open('sekai_best_borders.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','chapter','chara_id','type','name','unit','start_ms','end_ms','snapshot']+[f'r{k}' for k in RANKS], restval=''); w.writeheader(); w.writerows(out)
print('done', len(out))
