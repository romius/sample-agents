'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { runKind, runStatus, selectOwnRuns } from '../lib/run-presentation.mjs';

type Job = { id:string; document:string; author:string; state:string; name:string; trials:number; createdAt:string; startedAt:string|null; finishedAt:string|null; runId:string|null; sourceUrl:string; mine:boolean; completed?:number|null; failed?:number|null; score?:number|null; calls?:number; cost?:number; costComplete?:boolean; durationMinutes?:number };
type Row = { globalRank:number; name:string; account:string; score:number|null; duration:string; submitted:string };
type Snapshot = { brain:null|{ jobs:Job[]; queue:Job[]; own?:Job; ownBest?:Job; ownLatest?:Job; ownPosition:number; estimateMinutes:number|null; medianMinutes:number|null; durationSample:number; fetchedAt:string; baseline:{score:number|null;description:string;url:string} }; leaderboard:null|{rows:Row[];fetchedAt:string;sourceUrl:string}; errors:string[]; refreshedAt:string; refreshSeconds:number };
const source='https://brain.bitgn.com';
const labels:Record<string,string>={queued:'В очереди',running:'Выполняется',completed:'Завершён',failed:'Ошибка',interrupted:'Прерван',cancelled:'Отменён',cancelling:'Отменяется'};
const fmt=(n:number|null|undefined,d=2)=>n==null?'—':n.toLocaleString('ru-RU',{maximumFractionDigits:d,minimumFractionDigits:d});
const time=(s:string|null|undefined)=>s?new Date(s).toLocaleTimeString('ru-RU',{timeZone:'Europe/Berlin',hour:'2-digit',minute:'2-digit',second:'2-digit'}):'—';
const stamp=(s:string|null|undefined)=>s?new Date(s).toLocaleString('ru-RU',{timeZone:'Europe/Berlin',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}):'—';
const shortName=(s:string)=>s.replace(/^Brain\s+/,'');
const duration=(minutes:number|null|undefined)=>minutes==null?'—':minutes<1?'<1 мин':`${Math.round(minutes)} мин`;
const ago=(s:string|undefined,now:number)=>!s?'нет данных':`${Math.max(0,Math.floor((now-Date.parse(s))/1000))} с назад`;
function Arrow(){return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>}
function Refresh({spin=false}:{spin?:boolean}){return <svg className={spin?'spin':''} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-1l2 6M4 12l2 6a7 7 0 0 0 12-1"/></svg>}
function Badge({state}:{state:string}){return <span className={`badge ${state}`}><i/>{labels[state]||state}</span>}
function JobBadge({job}:{job:Job}){const status=runStatus(job);return <span className={`badge ${status.state}`}><i/>{status.label}</span>}
function RunType({job}:{job:Job}){const kind=runKind(job),n=job.trials,taskWord=n%10===1&&n%100!==11?'задача':n%10>=2&&n%10<=4&&(n%100<12||n%100>14)?'задачи':'задач';return <span className={`run-type ${kind}`} title={kind==='diagnostic'?'Диагностическое назначение указано в названии запуска. Его служебный балл не измеряет качество агента.':undefined}>{kind==='full'?'Full100 · 100 задач':kind==='diagnostic'?`Диагностика · ${job.trials} ${taskWord}`:kind==='short'?`Короткий тест · ${job.trials} ${taskWord}`:'Запуск'}</span>}
function JobScore({job,units=false}:{job:Job;units?:boolean}){const diagnostic=runKind(job)==='diagnostic';return <div className={diagnostic?'diagnostic-score':runStatus(job).state==='failed'?'failed-score':'score'}>{diagnostic?<><span>Не оценивается</span><small>Служебный балл Brain: {fmt(job.score)}</small></>:<>{fmt(job.score)}{units?<small className="score-unit">/100</small>:null}</>}</div>}
function JobCounts({job}:{job:Job}){return <div className="job-counts"><span>{job.completed??'—'} / {job.trials} обработано</span><small className={job.failed!=null&&job.failed>0?'has-errors':''}>Ошибки: {job.failed??'—'}</small></div>}
function Progress({j}:{j:Job}){const n=j.completed??0;return <><div className="progress" role="progressbar" aria-label="Завершённые задачи" aria-valuenow={n} aria-valuemin={0} aria-valuemax={j.trials}><span style={{width:`${Math.min(100,n/j.trials*100)}%`}}/></div><div className="progress-meta"><span>{n} / {j.trials} задач завершено</span><span>{j.failed==null?'Ошибки: —':`Ошибки: ${j.failed}`}</span></div></>}
function RunLink({job,compact=false}:{job:Job;compact?:boolean}){
 if(!job.mine||!job.runId?.startsWith('run-'))return null;
 return <a className={`bitgn-run-link ${compact?'compact':''}`} href={`https://eu.bitgn.com/runs/${encodeURIComponent(job.runId)}`} target="_blank" rel="noreferrer" title={job.runId} aria-label={`Открыть запуск ${job.name} в BitGN`}>Открыть запуск в BitGN <Arrow/></a>;
}
export default function Page(){
 const [data,setData]=useState<Snapshot|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[now,setNow]=useState(Date.now()),[search,setSearch]=useState(''),[mine,setMine]=useState(false),[tab,setTab]=useState('queue');
 const requestRef=useRef<AbortController|null>(null);
 const load=useCallback(async()=>{
  if(requestRef.current) return;
  const controller=new AbortController();
  requestRef.current=controller;
  const timer=setTimeout(()=>controller.abort(),25000);
  setBusy(true);
  try{
   const r=await fetch('/api/live',{cache:'no-store',signal:controller.signal});
   if(!r.ok)throw Error('Сервер временно недоступен. Можно повторить обновление.');
   const next=await r.json() as Snapshot & {error?:string};
   if(next.error)throw Error(next.error);
   if(requestRef.current!==controller)return;
   setData(previous=>({...next,brain:next.brain??previous?.brain??null,leaderboard:next.leaderboard??previous?.leaderboard??null}));
   setError('');
  }catch(e){
   if(requestRef.current===controller)setError(controller.signal.aborted?'Обновление превысило 25 секунд. Можно повторить; последние данные сохранены.':e instanceof Error?e.message:'Не удалось обновить данные.');
  }finally{
   clearTimeout(timer);
   if(requestRef.current===controller){requestRef.current=null;setBusy(false)}
  }
 },[]);
 useEffect(()=>{
  try{
   const saved=JSON.parse(sessionStorage.getItem('brain-live:last-success:v1')||'null') as Snapshot|null;
   if(saved?.brain?.fetchedAt&&Array.isArray(saved.brain.queue)&&Array.isArray(saved.errors))setData(saved);
  }catch{}
  load();
  const timer=setInterval(()=>{if(!document.hidden)load()},60000);
  const clock=setInterval(()=>setNow(Date.now()),1000);
  const visible=()=>{if(!document.hidden)load()};
  document.addEventListener('visibilitychange',visible);
  return()=>{clearInterval(timer);clearInterval(clock);document.removeEventListener('visibilitychange',visible);const request=requestRef.current;requestRef.current=null;request?.abort()};
 },[load]);
 useEffect(()=>{if(data?.brain){try{sessionStorage.setItem('brain-live:last-success:v1',JSON.stringify(data))}catch{}}},[data]);
 const b=data?.brain,p=data?.leaderboard,running=b?.queue.filter(j=>['running','cancelling'].includes(j.state))??[];
 const {ownBest,ownLatest}=selectOwnRuns(b?.jobs??[]) as {ownBest?:Job;ownLatest?:Job};
 const ownActiveQueue=(b?.queue??[]).map((j,index)=>({...j,position:index+1,ahead:index})).filter(j=>j.mine);
 const stale=!!error||!b||now-Date.parse(b.fetchedAt)>90000||!!data?.errors.length;
 const match=(s:string)=>s.toLowerCase().includes(search.toLowerCase());
 const queue=(b?.queue??[]).map((j,i)=>({...j,position:i+1})).filter(j=>match(`${j.name} ${j.author} ${j.id}`)&&(!mine||j.mine));
 const ranking=(p?.rows??[]).map((r,i)=>({...r,brainRank:i+1})).filter(r=>match(`${r.name} ${r.account}`)&&(!mine||/romius/i.test(r.name)));
 const history=(b?.jobs??[]).filter(j=>!['queued','running','cancelling'].includes(j.state)&&match(`${j.name} ${j.author} ${j.id}`)&&(!mine||j.mine));
 return <main>
 <header className="header"><div className="identity"><div className="mark" aria-hidden="true"><span/><span/><span/><span/></div><div><h1>Brain <span>Live</span></h1><p>ECOM1 · лаборатория агентов</p></div></div><div className="header-right"><span className={`live ${stale?'stale':''}`}><i/>{!data?(busy?'Подключение':'Нет связи'):stale?'Данные устарели':'Live · 60 с'}</span><button className="refresh" aria-label="Обновить данные" disabled={busy} onClick={load}><Refresh spin={busy}/><span>{busy?'Обновление…':'Обновить'}</span></button></div></header>
 <div className="intro"><div><p className="eyebrow">ОБЩИЙ ЭКСПЕРИМЕНТ</p><h2>Все запуски Brain.</h2></div><div className="source-time">Последние данные Brain<strong>{time(b?.fetchedAt)} <small>Берлин</small></strong><span>{ago(b?.fetchedAt,now)}</span></div></div>
 {(error||data?.errors.length)?<div className="alert" role="status">{error||data?.errors.join(' ')} Время последнего успешного обновления указано у источников.</div>:null}
 <section className="metrics" aria-label="Сводка"><a className="metric" href={b?.baseline.url||`${source}/#w=1&d=7`} target="_blank" rel="noreferrer"><span>Рабочий рекорд лаборатории <Arrow/></span><strong>{fmt(b?.baseline.score)}<small>/100</small></strong><p>Из agent/BASELINE.md</p></a><div className="metric queue-metric"><span>Активная очередь</span><strong>{b?b.queue.filter(j=>j.state==='queued').length:'—'}<small>ожидают</small></strong><p>{b?running.length:'—'} выполняется сейчас</p><div className="own-queue-summary" aria-label="Наши запуски в активной очереди"><div className="own-queue-heading">Наши запуски <span>romius</span></div>{ownActiveQueue.length?ownActiveQueue.map(j=><div className="own-queue-entry" key={j.id}><a className="own-queue-item" href={j.sourceUrl} target="_blank" rel="noreferrer" title={j.state==='queued'?`Позиция ${j.position} в общей очереди; ${j.ahead} запусков впереди, включая выполняющийся.`:labels[j.state]||j.state}><span className={`own-queue-rank ${j.state==='queued'?'':'active'}`}>{j.state==='queued'?`№ ${j.position}`:'↗'}</span><span className="own-queue-copy"><span className="own-queue-name">{j.name}</span><small>{j.state==='queued'?`${j.ahead} запусков впереди · ${j.trials} задач`:labels[j.state]||j.state}</small></span><Arrow/></a><RunLink job={j} compact/></div>):<p className="own-queue-empty">{b?'Наших запусков в активной очереди нет':'Позиции появятся после загрузки данных'}</p>}{ownActiveQueue.some(j=>j.state==='queued')?<p className="own-queue-footnote">Позиция включает выполняющийся запуск.</p>:null}</div></div><div className="metric"><span>Медиана полного прогона</span><strong>{b?.medianMinutes?Math.round(b.medianMinutes):'—'}<small>мин</small></strong><p>{b?.durationSample??'—'} завершённых full100 в доступной истории</p></div></section>
 <section className="activity activity-overview" aria-label="Прогресс и наши запуски">
 <div className="panel active-panel"><div className="panel-top"><h3><span className="activity-dot"/>Сейчас выполняется</h3><span className="running-count">{b?running.length:'—'} запусков</span></div>
 {running.length?<div className="running-list">{running.map(j=><article className={`running-item ${j.mine?'our-running-item':''}`} key={j.id} aria-label={`Выполняющийся запуск ${j.name}`}><div className="running-item-top"><RunType job={j}/><JobBadge job={j}/></div><a className="run-title" href={j.sourceUrl} target="_blank" rel="noreferrer">{j.name}<Arrow/></a><div className="run-sub"><span>{j.mine?'romius · наш запуск':j.author}</span><span>Старт {time(j.startedAt)}</span><span>{j.startedAt?`${duration((now-Date.parse(j.startedAt))/60000)} в работе`:'Время старта недоступно'}</span></div><Progress j={j}/><RunLink job={j}/></article>)}</div>:<div className="empty-card">{b?'Нет выполняющихся запусков':busy?'Загружаем очередь и прогресс…':'Данные пока недоступны. Попробуйте обновить.'}</div>}
 </div>
 <div className="own-run-cards">
 <div className="panel mine-panel best-panel"><div className="panel-top"><h3>Наш лучший запуск <span className="tiny">romius</span></h3>{ownBest?<JobBadge job={ownBest}/>:null}</div><p className="card-scope">Лучший завершённый full100 в доступной истории Brain</p>
 {ownBest?<><a className="run-title" href={ownBest.sourceUrl} target="_blank" rel="noreferrer">{ownBest.name}<Arrow/></a><div className="own-result"><JobScore job={ownBest} units/><div className="own-result-meta">Завершён {stamp(ownBest.finishedAt)}<JobCounts job={ownBest}/></div></div><RunLink job={ownBest}/></>:<div className="empty-card">{b?'В доступной истории пока нет нашего оценённого full100':'Загружаем лучший результат…'}</div>}
 </div>
 <div className="panel mine-panel latest-panel"><div className="panel-top"><h3>Наш последний запуск <span className="tiny">romius</span></h3>{ownLatest?<JobBadge job={ownLatest}/>:null}</div><p className="card-scope">Последний по времени отправки · независимо от статуса и типа</p>
 {ownLatest?<><a className="run-title" href={ownLatest.sourceUrl} target="_blank" rel="noreferrer">{ownLatest.name}<Arrow/></a><RunType job={ownLatest}/><div className="run-sub"><span>Отправлен {stamp(ownLatest.createdAt)}</span>{ownLatest.startedAt?<span>Старт {time(ownLatest.startedAt)}</span>:null}</div>
 {ownLatest.state==='queued'?<><div className="queue-number"><strong>{b!.queue.findIndex(j=>j.id===ownLatest.id)+1||'—'}</strong><span>позиция в общей очереди</span></div><div className="queue-note">{b!.queue.findIndex(j=>j.id===ownLatest.id)>=0?`${b!.queue.findIndex(j=>j.id===ownLatest.id)} запусков впереди, включая выполняющиеся.`:'Ожидает запуска.'}</div></>:['running','cancelling'].includes(ownLatest.state)?<Progress j={ownLatest}/>:<div className="own-result"><JobScore job={ownLatest} units/><div className="own-result-meta">{ownLatest.finishedAt?`Завершён ${stamp(ownLatest.finishedAt)}`:labels[ownLatest.state]||ownLatest.state}<JobCounts job={ownLatest}/></div></div>}<RunLink job={ownLatest}/></>:<div className="empty-card">{b?'Наших запусков в доступной истории нет':'Загружаем последний запуск…'}</div>}
 </div></div></section>
 <section className="workspace"><div className="workspace-header"><nav aria-label="Представление"><button className={tab==='queue'?'selected':''} onClick={()=>setTab('queue')}>Очередь <span>{b?.queue.length??'—'}</span></button><button className={tab==='ranking'?'selected':''} onClick={()=>setTab('ranking')}>Рейтинг Brain <span>{p?.rows.length??'—'}</span></button><button className={tab==='history'?'selected':''} onClick={()=>setTab('history')}>Последние</button></nav><div className="filters"><input aria-label="Поиск запусков" placeholder="Поиск по имени или автору…" value={search} onChange={e=>setSearch(e.target.value)}/><label><input type="checkbox" checked={mine} onChange={e=>setMine(e.target.checked)}/>Только romius</label></div></div>
 <div className="table-note">{tab==='queue'?<>Живая очередь Brain · позиции сохраняются при фильтрации · обновлено {time(b?.fetchedAt)}</>:tab==='ranking'?<>Только записи «Brain» из публичного рейтинга · лучший результат каждого аккаунта · {time(p?.fetchedAt)}</>:<>Последние 25 запусков и наши из доступной истории · «Завершён» означает окончание прогона · ошибки выполнения указаны отдельно. Диагностика определяется по названию; её служебный балл не оценивает качество агента.</>}</div>
 <div className="table-wrap"><table><thead><tr>{tab==='ranking'?<><th>Место Brain</th><th>Эксперимент</th><th>Аккаунт</th><th className="right">Баллы /100</th><th>Время</th><th>Публикация</th></>:<><th>{tab==='queue'?'Позиция':'Статус'}</th><th>Эксперимент</th><th>Автор</th><th>{tab==='queue'?'Состояние':'Баллы /100'}</th>{tab==='history'?<th>Задачи / ошибки</th>:null}<th>{tab==='queue'?'Прогресс':'Длительность'}</th><th>{tab==='queue'?'В очереди с':'Завершён'}</th></>}</tr></thead><tbody>
 {tab==='ranking'?ranking.map(r=><tr key={`${r.globalRank}-${r.account}`} className={/romius/i.test(r.name)?'own-row':''}><td className="rank">{r.brainRank}<small>#{r.globalRank} общий</small></td><td className="name-cell">{shortName(r.name)}</td><td><code>{r.account}</code></td><td className="score right">{fmt(r.score,1)}</td><td className="mono">{r.duration}</td><td className="muted">{r.submitted}</td></tr>):tab==='queue'?queue.map(j=><tr key={j.id} className={j.mine?'own-row':''}><td className="rank">{j.state==='running'?<span className="running-glyph">↗</span>:j.position}<small>{j.mine?'наш запуск':`${j.trials} задач`}</small></td><td className="name-cell"><a href={j.sourceUrl} target="_blank" rel="noreferrer">{j.name}<Arrow/></a><RunType job={j}/><code className="job-id" title={j.id}>{j.id.slice(0,13)}</code><RunLink job={j} compact/></td><td>{j.author}</td><td><JobBadge job={j}/></td><td className="mono">{j.state==='queued'?'—':`${j.completed??'—'} / ${j.trials}`}</td><td className="mono muted">{time(j.createdAt)}</td></tr>):history.map(j=><tr key={j.id} className={`${j.mine?'own-row ':''}${runStatus(j).state==='failed'?'run-failed':''}`}><td><JobBadge job={j}/></td><td className="name-cell"><a href={j.sourceUrl} target="_blank" rel="noreferrer">{j.name}<Arrow/></a><RunType job={j}/><code className="job-id" title={j.id}>{j.id.slice(0,13)}</code><RunLink job={j} compact/></td><td>{j.author}</td><td><JobScore job={j}/></td><td><JobCounts job={j}/></td><td className="mono">{duration(j.durationMinutes)}</td><td className="mono muted">{time(j.finishedAt)}</td></tr>)}
 {((tab==='ranking'&&!ranking.length)||(tab==='queue'&&!queue.length)||(tab==='history'&&!history.length))?<tr><td className="table-empty" colSpan={tab==='history'?7:6}>{!data?(busy?'Получаем данные из источников…':'Данные не получены. Нажмите «Обновить».'):mine?'Подходящих запусков romius в этом представлении пока нет.':'Нет записей по выбранному фильтру.'}</td></tr>:null}
 </tbody></table></div></section>
 <footer><details><summary>Источники и обновление</summary><div className="source-grid"><div><strong>Brain MCP</strong><p>Очередь, статус, прогресс, последние запуски и рабочий рекорд.</p><p>Успешно получено: {time(b?.fetchedAt)} · {ago(b?.fetchedAt,now)}</p><a href={`${source}/#w=1&d=7`} target="_blank" rel="noreferrer">Открыть baseline <Arrow/></a></div><div><strong>Публичный лидерборд</strong><p>Фильтр по префиксу Brain. Рейтинг объединяет разные аккаунты; это не история всех запусков.</p><p>Успешно получено: {time(p?.fetchedAt)} · {ago(p?.fetchedAt,now)}</p><a href="https://bitgn.com/l/ecom1-prod" target="_blank" rel="noreferrer">Открыть источник <Arrow/></a></div><div><strong>Что означает Live</strong><p>Обновление каждые 60 секунд, пока страница открыта и видима. Оценки до завершения прогона не показываются. При сбое остаются прежние данные с их временем.</p><p>Баллы /100 учитывают частичное выполнение; это не процент полностью решённых задач. Все часы — Europe/Berlin.</p></div></div></details><span>BitGN / ECOM1</span></footer>
 </main>
}
