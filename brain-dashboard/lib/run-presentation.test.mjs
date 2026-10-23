import test from 'node:test';
import assert from 'node:assert/strict';
import {runKind,runStatus,selectOwnRuns} from './run-presentation.mjs';

test('diagnostic intent is explicit, never inferred from a low score or trial count',()=>{
 assert.equal(runKind({trials:1,name:'romius C/L lexical-label diagnostic; no carrier score'}),'diagnostic');
 assert.equal(runKind({trials:1,name:'romius zero-LLM SDK boundary probe'}),'diagnostic');
 assert.equal(runKind({trials:1,name:'single task evaluation'}),'short');
 assert.equal(runKind({trials:19,name:'smoke19'}),'short');
 assert.equal(runKind({trials:100,name:'full100 with diagnostic logging'}),'full');
});

test('completion never hides task execution failures or invents failures from zero grades',()=>{
 assert.deepEqual(runStatus({state:'completed',trials:100,failed:100}),{state:'failed',label:'Все задачи упали'});
 assert.equal(runStatus({state:'completed',trials:100,failed:1}).state,'with-errors');
 assert.equal(runStatus({state:'completed',trials:100,failed:0}).state,'completed');
 assert.equal(runStatus({state:'completed',trials:100}).label,'Завершён');
 assert.equal(runStatus({state:'running',trials:100,failed:1}).state,'running');
 assert.equal(runStatus({state:'cancelled',trials:100}).state,'cancelled');
});

test('best is a graded complete own full100; latest follows submission time regardless of state',()=>{
 const job=(id,changes={})=>({id,mine:true,state:'completed',trials:100,completed:100,score:83.1,createdAt:'2026-10-22T12:00:00Z',...changes});
 const jobs=[job('original'),job('best',{score:87.11}),job('other',{mine:false,score:99}),job('diagnostic',{trials:1,score:100,createdAt:'2026-10-23T09:00:00Z'}),job('short',{trials:19,score:95}),job('pending',{completed:80,score:99}),job('ungraded',{score:null}),job('first-running',{state:'running',score:null,createdAt:'2026-10-23T04:00:00Z'}),job('newest-running',{state:'running',score:null,createdAt:'2026-10-23T05:00:00Z'})];
 const selected=selectOwnRuns(jobs);
 assert.equal(selected.ownBest.id,'best');assert.equal(selected.ownLatest.id,'diagnostic');
 assert.equal(jobs[0].id,'original');
 const noRunning=selectOwnRuns(jobs.filter(j=>j.state!=='running'));
 assert.equal(noRunning.ownLatest.id,'diagnostic');assert.equal(noRunning.ownBest.id,'best');
 const newerQueued=job('latest-queued',{state:'queued',score:null,createdAt:'2026-10-23T10:00:00Z'});
 assert.equal(selectOwnRuns([...jobs,newerQueued]).ownLatest.id,'latest-queued');
});

test('no own runs and no evaluated full100 remain honest empty states',()=>{
 assert.deepEqual(selectOwnRuns([]),{ownBest:undefined,ownLatest:undefined});
 assert.equal(selectOwnRuns([{mine:true,state:'queued',trials:100,createdAt:'2026-10-23T12:00:00Z'}]).ownBest,undefined);
 const zero={mine:true,state:'completed',trials:100,completed:100,score:0};
 assert.equal(selectOwnRuns([zero]).ownBest,zero);
});
