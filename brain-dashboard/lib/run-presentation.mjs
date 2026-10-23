// Short runs are diagnostics only when their name explicitly says so.
// A low score, a single trial or zero model calls does not establish intent.
/** @param {{trials?:number,name?:string}} job */
export function runKind(job) {
  if (job.trials === 100) return 'full';
  if (/\b(?:diagnostic|probe)\b|диагност/i.test(job.name || '')) return 'diagnostic';
  return job.trials > 0 && job.trials < 100 ? 'short' : 'unknown';
}

/** @param {{state:string,trials?:number,failed?:number|null}} job */
export function runStatus(job) {
  if (job.state === 'completed' && job.trials > 0 && job.failed >= job.trials)
    return {state:'failed',label:'Все задачи упали'};
  if (job.state === 'completed' && job.failed > 0)
    return {state:'with-errors',label:'Завершён с ошибками'};
  const labels = {queued:'В очереди',running:'Выполняется',completed:'Завершён',failed:'Ошибка',interrupted:'Прерван',cancelled:'Отменён',cancelling:'Отменяется'};
  return {state:job.state,label:labels[job.state] || job.state};
}

/** @template {{mine?:boolean,state:string,trials?:number,score?:number|null,completed?:number|null,createdAt?:string|null,startedAt?:string|null,finishedAt?:string|null}} T
 * @param {T[]} jobs
 */
export function selectOwnRuns(jobs) {
  const created = j => Date.parse(j.createdAt || j.startedAt || j.finishedAt || '') || 0;
  const own = jobs.filter(j => j.mine).sort((a,b) => created(b)-created(a));
  const best = own.filter(j => j.state==='completed' && j.trials===100 && j.completed>=100 && Number.isFinite(j.score))
    .sort((a,b) => b.score-a.score || created(b)-created(a))[0];
  return {ownBest:best, ownLatest:own[0]};
}
