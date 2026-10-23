import { BRAIN_SOURCE, LEADERBOARD_URL, parseLeaderboard, normalizeBrain } from './live-data.mjs';

async function rpc(endpoint, method, params, sessionHeader, signal) {
  const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type':'application/json', Accept:'application/json, text/event-stream', ...(sessionHeader ? { 'Mcp-Session-Id':sessionHeader } : {}) },
    body: JSON.stringify({ jsonrpc:'2.0', id:1, method, params }), signal:signal ? AbortSignal.any([signal, AbortSignal.timeout(10000)]) : AbortSignal.timeout(10000) });
  if (!response.ok) throw new Error('Brain connection unavailable.');
  const body = await response.text();
  let message;
  if (body.trim().startsWith('{')) message = JSON.parse(body);
  else {
    const events = body.split('\n').filter(l => l.startsWith('data:')).map(l => JSON.parse(l.slice(5)));
    message = events.find(e => e.id === 1);
  }
  if (!message || message.error) throw new Error('Brain request was rejected.');
  return { result:message.result, session:response.headers.get('Mcp-Session-Id') || sessionHeader };
}
function structured(result) {
  const value = result.structuredContent || JSON.parse(result.content.find(c=>c.type==='text').text);
  if (result.isError || value.code !== 0) throw new Error('Brain data request failed.');
  return value;
}
export async function readBrain(endpoint, signal) {
  const init = await rpc(endpoint, 'initialize', {protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'brain-live-readonly',version:'1.1'} }, undefined, signal);
  const started = structured((await rpc(endpoint,'tools/call',{name:'brain_start',arguments:{task:'Read-only live dashboard refresh: queue, recent results and baseline. No document edits or benchmark submissions.'}},init.session, signal)).result);
  const args = { session:started.data.session, seq:started.data.next_seq, source:BRAIN_SOURCE };
  let response;
  try { response = await rpc(endpoint,'tools/call',{name:'brain_run',arguments:args},init.session, signal); }
  catch (error) {
    if (signal?.aborted) throw error;
    response = await rpc(endpoint,'tools/call',{name:'brain_run',arguments:args},init.session, signal);
  }
  const run = structured(response.result);
  if (run.data.output_truncated) throw new Error('Brain snapshot exceeded the output limit.');
  const line = run.output.split('\n').find(l=>l.startsWith('{"jobs":'));
  if (!line) throw new Error('Brain snapshot unavailable.');
  return { ...normalizeBrain(JSON.parse(line)), fetchedAt:new Date().toISOString() };
}
async function readPublic(_endpoint, signal) {
  const response = await fetch(LEADERBOARD_URL, { signal,headers:{'Cache-Control':'no-cache'} });
  if (!response.ok) throw new Error('Public leaderboard unavailable.');
  return { rows:parseLeaderboard(await response.text()), fetchedAt:new Date().toISOString(), sourceUrl:LEADERBOARD_URL };
}
function withDeadline(read, endpoint, milliseconds) {
  const controller = new AbortController();
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => {
      controller.abort();
      reject(new Error('Source deadline exceeded.'));
    }, milliseconds);
  });
  return Promise.race([Promise.resolve().then(() => read(endpoint, controller.signal)), timeout]).finally(() => clearTimeout(timer));
}

// Cloudflare cancels request-scoped I/O when its request ends. Never retain a
// pending promise across requests: a canceled owner can strand later visitors.
// Only fully resolved source values may live in the isolate-level cache.
export function createLiveReader({brainReader=readBrain, publicReader=readPublic, deadlineMs=18000, cacheMs=30000}={}) {
  let cached = null;
  let lastBrain = null;
  let lastPublic = null;
  return async function getSnapshot(endpoint) {
    if (cached && Date.now()-cached.created < cacheMs) return cached.value;
    const [brain, leaderboard] = await Promise.allSettled([
      endpoint ? withDeadline(brainReader, endpoint, deadlineMs) : Promise.reject(new Error('Brain connection is not configured.')),
      withDeadline(publicReader, endpoint, Math.min(deadlineMs, 10000))
    ]);
    const errors = [];
    if (brain.status==='fulfilled') lastBrain=brain.value; else errors.push('Brain: источник временно недоступен. Повторите обновление.');
    if (leaderboard.status==='fulfilled') lastPublic=leaderboard.value; else errors.push('Публичный рейтинг: обновление не удалось.');
    const value = { brain:lastBrain, leaderboard:lastPublic, errors, refreshedAt:new Date().toISOString(), refreshSeconds:60 };
    if (brain.status==='fulfilled' && leaderboard.status==='fulfilled') cached={created:Date.now(),value};
    return value;
  };
}
export const getLiveSnapshot = createLiveReader();
