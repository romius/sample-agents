import {selectOwnRuns} from './run-presentation.mjs';
export const LEADERBOARD_URL = 'https://bitgn.com/l/ecom1-prod';
export const WATCHED_JOB = 'jd8713c77f6ab4a0e9f67bcd614d8d2e9';

export function decodeHtml(s) {
  return s.replace(/&#(x[\da-f]+|\d+);/gi, (_, n) => String.fromCodePoint(n[0].toLowerCase() === 'x' ? parseInt(n.slice(1), 16) : +n))
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ');
}
const plain = s => decodeHtml(s.replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim();

export function parseLeaderboard(html) {
  const rows = [];
  for (const row of html.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)) {
    const cells = [...row[1].matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/gi)].map(x => plain(x[1]));
    if (cells.length < 6 || !/^Brain\s/i.test(cells[1])) continue;
    const score = /^([\d.]+)\s*\/\s*100/.exec(cells[3]);
    rows.push({ globalRank: Number(cells[0]), name: cells[1], account: cells[2], score: score ? Number(score[1]) : null, duration: cells[4], submitted: cells[5] });
  }
  if (!rows.length) throw new Error('Leaderboard markup changed or Brain entries are unavailable.');
  return rows;
}

export function unpackJob(row) {
  const [id, document, author, state, name, trials, createdAt, startedAt, finishedAt, runId] = row;
  return { id, document, author, state, name, trials, createdAt, startedAt, finishedAt, runId,
    sourceUrl: `https://brain.bitgn.com/#w=1&d=${document.replace(/^d/, '')}`, mine: author === 'romius' };
}

export function normalizeBrain(raw) {
  const jobs = raw.jobs.map(unpackJob);
  const summaries = raw.summaries || {};
  for (const j of jobs) {
    const s = summaries[j.id];
    if (s) Object.assign(j, { score: typeof s.score === 'number' ? s.score * 100 : null, completed: s.completed, failed: s.failed, calls: s.calls, cost: s.cost, costComplete: s.costComplete });
    if (j.startedAt && j.finishedAt) j.durationMinutes = (Date.parse(j.finishedAt) - Date.parse(j.startedAt)) / 60000;
  }
  const queue = raw.queue.map(id => jobs.find(j => j.id === id)).filter(Boolean);
  const durations = jobs.filter(j => j.state === 'completed' && j.trials === 100 && j.durationMinutes > 0).map(j => j.durationMinutes).sort((a,b) => a-b);
  const median = durations.length ? (durations[Math.floor((durations.length-1)/2)] + durations[Math.floor(durations.length/2)]) / 2 : null;
  const {ownBest,ownLatest} = selectOwnRuns(jobs);
  const own = ownLatest;
  let estimateMinutes = null;
  const ownPosition = own ? queue.findIndex(j => j.id === own.id) : -1;
  if (median && ownPosition > 0) {
    estimateMinutes = queue.slice(0, ownPosition).reduce((sum, j) => {
      const predicted = median * j.trials / 100;
      return sum + (j.startedAt ? Math.max(0, predicted - (Date.now() - Date.parse(j.startedAt))/60000) : predicted);
    }, 0);
  }
  const match = /\*\*([\d.]+)\/100\s*[—-]\s*([^\n]+)/.exec(raw.baseline);
  return { jobs, queue, own, ownBest, ownLatest, ownPosition, estimateMinutes, medianMinutes: median, durationSample: durations.length,
    baseline: { score: match ? Number(match[1]) : null, description: match ? match[2].replace(/\*\*/g, '') : raw.baseline, url: 'https://brain.bitgn.com/#w=1&d=7' } };
}

export const BRAIN_SOURCE = `import json
brain.workspace("w1")
queue = brain.sandbox.queue()
recent = brain.sandbox.runs(limit=100)
qids = {j["id"] for j in queue}
done = [j for j in recent if j["id"] not in qids][:25]
known = qids | {j["id"] for j in done}
own_recent = [j for j in recent if j.get("author") == "romius" and j["id"] not in known]
jobs = queue + done + own_recent
watched = "${WATCHED_JOB}"
if not any(j["id"] == watched for j in jobs):
    jobs.append(brain.sandbox.status(watched))
def pack(j):
    return [j["id"],j["document"],j.get("author"),j["state"],j.get("name", "")[:160],j.get("trial_count"),j.get("created_at"),j.get("started_at"),j.get("finished_at"),j.get("run_id")]
summaries = {}
targets = [j for j in queue if j["state"] != "queued"] + [j for j in jobs if j["state"] in ("completed", "failed", "interrupted") and j["id"] not in qids]
for j in jobs:
    if j["id"] == watched and j["state"] != "queued" and not any(x["id"] == watched for x in targets):
        targets.append(j)
for j in targets:
    r = brain.sandbox.result(j["id"]).get("result") or {}
    score = r.get("run_score") if r.get("run_score_available", True) else None
    summaries[j["id"]] = {"score":score,"completed":r.get("completed_trials"),"failed":r.get("failed_trials"),"calls":r.get("model_calls"),"cost":r.get("model_cost_usd"),"costComplete":r.get("cost_complete")}
baseline = brain.read("w1:agent/BASELINE.md")[:650]
print(json.dumps({"jobs":[pack(j) for j in jobs],"queue":[j["id"] for j in queue],"summaries":summaries,"baseline":baseline},separators=(",",":")))
brain.discard()
`;
