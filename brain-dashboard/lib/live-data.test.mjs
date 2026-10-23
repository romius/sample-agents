import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {parseLeaderboard, normalizeBrain, BRAIN_SOURCE} from './live-data.mjs';

test('leaderboard includes only Brain prefix, decodes entities and preserves ungraded/disqualified scores',()=>{
 const row=c=>'<tr>'+c.map(x=>'<td>'+x+'</td>').join('')+'</tr>';
 const data=parseLeaderboard(row(['1','Other Brain experiment','u','99.1/100','1:00','today'])+row(['2','Brain A &#43; B','abc x2','79.7/100','12:36','today'])+row(['3','Brain invalid','def','DISQUALIFY','1:00','today']));
 assert.equal(data.length,2);assert.equal(data[0].name,'Brain A + B');assert.equal(data[0].score,79.7);assert.equal(data[1].score,null);
});
test('queue preserves actual positions, official score units and completed zero values',()=>{
 const first=['j1','d1','other','running','first',100,'2026-10-22T12:00:00Z','2026-10-22T12:01:00Z',null,null];
 const mine=['jd8713c77f6ab4a0e9f67bcd614d8d2e9','d2','romius','queued','ours',100,'2026-10-22T12:00:00Z',null,null,null];
 const done=['j3','d3','other','completed','done',100,'2026-10-22T11:00:00Z','2026-10-22T11:30:00Z','2026-10-22T11:45:00Z','r1'];
 const data=normalizeBrain({jobs:[first,mine,done],queue:['j1',mine[0]],summaries:{j1:{completed:0,failed:0},j3:{score:.7974685,completed:100,failed:1}},baseline:'**79.74685/100 — source**'});
 assert.equal(data.ownPosition,1);assert.equal(data.queue[0].completed,0);assert.ok(Math.abs(data.jobs[2].score-79.74685)<1e-10);assert.equal(data.medianMinutes,15);assert.equal(data.baseline.score,79.74685);
 assert.equal(data.queue[0].score,null);assert.equal(data.own.mine,true);
});
test('snapshot program only reads and closes its session',()=>{
 assert.match(BRAIN_SOURCE,/brain\.discard\(\)/);assert.doesNotMatch(BRAIN_SOURCE,/brain\.(create|write|edit|commit)\(|sandbox\.(submit|cancel)\(/);
});

test('snapshot fetches all displayed completed results beyond ten, preserving unavailable and zero scores',()=>{
 const fixture = `
class Sandbox:
    def queue(self): return []
    def runs(self, limit):
        return [{"id":"j"+str(i),"document":"d1","state":"completed","trial_count":100} for i in range(25)] + [
            {"id":"own-older","document":"d4702","author":"romius","state":"completed","trial_count":100},
            {"id":"own-crash","document":"d5204","author":"romius","state":"completed","trial_count":100},
            {"id":"other-older","document":"d2","author":"other","state":"completed","trial_count":100}]
    def status(self, job): return {"id":job,"document":"d2499","author":"romius","state":"completed","trial_count":100}
    def result(self, job):
        if job == "own-crash": return {"result":{"run_score":0,"run_score_available":True,"completed_trials":100,"failed_trials":100}}
        if job == "j23": return {"result":{"run_score":0,"run_score_available":False}}
        if job == "j24": return {"result":{"run_score":0,"run_score_available":True}}
        return {"result":{"run_score":0.8,"run_score_available":True,"completed_trials":100}}
class Brain:
    sandbox=Sandbox()
    def workspace(self, ref): pass
    def read(self, ref): return "**80/100 — fixture**"
    def discard(self): pass
brain=Brain()
`;
 const raw=JSON.parse(execFileSync('python3',['-c',fixture+BRAIN_SOURCE],{encoding:'utf8'}));
 const data=normalizeBrain(raw);
 assert.equal(Object.keys(raw.summaries).length,28);
 assert.equal(data.jobs.find(j=>j.id==='own-older').score,80);
 assert.equal(data.jobs.find(j=>j.id==='own-crash').failed,100);
 assert.equal(data.jobs.find(j=>j.id==='own-crash').score,0);
 assert.equal(data.jobs.find(j=>j.id==='other-older'),undefined);
 assert.equal(data.jobs.find(j=>j.id==='j22').score,80);
 assert.equal(data.jobs.find(j=>j.id==='j23').score,null);
 assert.equal(data.jobs.find(j=>j.id==='j24').score,0);
 assert.equal(data.own.score,80);
});

test('our completed run remains visible after it leaves the queue',()=>{
 const id='jd8713c77f6ab4a0e9f67bcd614d8d2e9';
 const raw={jobs:[[id,'d2499','romius','completed','ours',100,'2026-10-22T08:56:42Z','2026-10-22T12:40:11Z','2026-10-22T12:56:18Z','run-id']],queue:[],summaries:{[id]:{score:.83099496,completed:100,failed:1}},baseline:'**83.099496/100 — romius**'};
 const data=normalizeBrain(raw);
 assert.equal(data.queue.length,0);assert.equal(data.own.id,id);assert.equal(data.own.state,'completed');assert.equal(data.own.completed,100);assert.equal(data.own.failed,1);assert.equal(data.ownPosition,-1);
 assert.ok(Math.abs(data.own.score-83.099496)<1e-10);
});
