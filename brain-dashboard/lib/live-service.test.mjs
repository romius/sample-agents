import test from 'node:test';
import assert from 'node:assert/strict';
import {createLiveReader} from './live-service.mjs';

const brain = () => ({fetchedAt:new Date().toISOString(),queue:[],own:{state:'completed',score:83.099496}});
const leaderboard = () => ({fetchedAt:new Date().toISOString(),rows:[{name:'Brain romius',score:83.1}]});

test('a stalled request cannot strand the next request in the Worker isolate',async()=>{
 let calls=0, firstAborted=false;
 const read=createLiveReader({cacheMs:0,deadlineMs:60,publicReader:async()=>leaderboard(),brainReader:async(_endpoint,signal)=>{
  if(++calls===1){signal.addEventListener('abort',()=>{firstAborted=true});return new Promise(()=>{})}
  return brain();
 }});
 const stalled=read('configured');
 await new Promise(resolve=>setTimeout(resolve,5));
 const next=await read('configured');
 assert.equal(next.brain.own.state,'completed');assert.equal(next.errors.length,0);
 await stalled;
 assert.equal(firstAborted,true);assert.equal(calls,2);
});

test('a source timeout returns the other source, and subsequent refresh recovers',async()=>{
 let broken=true;
 const read=createLiveReader({cacheMs:0,deadlineMs:15,publicReader:async()=>leaderboard(),brainReader:async()=>{
  if(broken)return new Promise(()=>{});
  return brain();
 }});
 const partial=await read('configured');
 assert.equal(partial.brain,null);assert.equal(partial.leaderboard.rows.length,1);assert.equal(partial.errors.length,1);
 broken=false;
 const recovered=await read('configured');assert.equal(recovered.brain.own.score,83.099496);assert.equal(recovered.errors.length,0);
});

test('last successful data keeps its original timestamp after a refresh fails',async()=>{
 let broken=false;
 const old=brain();
 const read=createLiveReader({cacheMs:0,deadlineMs:15,publicReader:async()=>leaderboard(),brainReader:async()=>{
  if(broken)throw Error('temporarily offline');return old;
 }});
 await read('configured');broken=true;
 const stale=await read('configured');assert.equal(stale.brain,old);assert.equal(stale.brain.fetchedAt,old.fetchedAt);assert.equal(stale.errors.length,1);
});
