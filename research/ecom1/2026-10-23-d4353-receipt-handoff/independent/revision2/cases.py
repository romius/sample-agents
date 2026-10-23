# Runs after the exact pressure helper and parent observation definitions.
def size(x):return len(json.dumps(x).encode('utf-8'))
def trim(messages,bc):
 while size(messages)>56000 and len(messages)>bc+2:messages=messages[:bc]+messages[bc+2:]
 return messages
results=[]
for added in [0,1,2]:
 base=[{'role':'system','content':'policy'},{'role':'user','content':'b'*44000}]
 extra=[{'role':'user','content':'receipt-'+str(i)+'x'*4400} for i in range(added)]
 suffix=[{'role':'assistant','content':'next'},{'role':'user','content':'中'*2200}]
 before=base+extra+suffix;bc=len(base)+added
 out,b,a=receipt_pressure(before,bc,added)
 if added and size(before)>56000:
  assert out==base+suffix and b==len(base) and a==0
 else:assert out is before and b==bc and a==added
 assert receipt_pressure(out,b,a)==(out,b,a)
 assert trim(out,b)==trim(base+suffix,len(base))
 results.append({'case':'pressure_count_'+str(added),'before_bytes':size(before),'after_bytes':size(out),'added_after':a,'exact_parent_history_after_pressure':out==base+suffix})
# Exact initial review history-counterexample byte sizes.
base=[{'role':'system','content':'policy'},{'role':'user','content':'b'*44000}]
policy={'path':'/docs/availability-checks.md','content':'max(on_hand - reserved, 0); absent from a branch inventory','sha256':'d785fe1b99bf5b4a5e83e2c8e6a43b7af45cc2a79d3198942b20d6add8c7ee2a','contentType':'text/plain'}
upload={'path':'/uploads/receipt.txt','content':'x'*8900,'sha256':'a'*64,'contentType':'text/plain'}
RECEIPT_PENDING=[]
assert receipt_capture(policy['path'],policy) and receipt_capture(upload['path'],upload)
handed=receipt_handoff(base)
f={'tool':'read','path':'/docs/next.txt'}
pair=[{'role':'assistant','content':json.dumps(f)},{'role':'user','content':observation(f,{'content':'中'*2200})}]
old_candidate=handed+pair;out,bc,added=receipt_pressure(old_candidate,len(handed),len(handed)-len(base))
assert size(old_candidate)==66961 and size(out)==57447 and out==base+pair
assert trim(out,bc)==trim(base+pair,len(base))
results.append({'case':'original_new_overflow_resolved','initial_candidate_bytes':size(old_candidate),'revised_bytes':size(out),'parent_bytes':size(base+pair),'exact_parent_messages':True})
# Benign transfer is byte-identical; no eager evidence removal.
small=[{'role':'system','content':'policy'},{'role':'user','content':'question'}]+handed[2:]
out,bc,added=receipt_pressure(small,len(small),2);assert out is small and added==2 and bc==len(small)
results.append({'case':'benign_identical','bytes':size(out),'unchanged':True})
# Forced report can itself trigger pressure; exact source marker survives removal.
forced={'role':'user','content':'Stop working now. Reply with report_completion only: the best supported answer, the matching outcome and the exact refs you read.'}
# Padding is a history observation; transfer remains contiguous before suffix.
threshold_base=[{'role':'system','content':'x'*45000}]
extra=[{'role':'user','content':'y'*5000},{'role':'user','content':'z'*5000}]
suffix=[{'role':'assistant','content':'act'},{'role':'user','content':'w'*700}]
before=threshold_base+extra+suffix
while size(before)+size(forced)+2<=56000:before[-1]['content']+='w'
assert size(before)<=56000<size(before+[forced])
out,bc,added=receipt_pressure(before+[forced],3,2)
assert out==threshold_base+suffix+[forced] and out[-1]==forced and bc==1 and added==0
results.append({'case':'forced_append_crosses_threshold','before_bytes':size(before),'with_stop_bytes':size(before+[forced]),'after_bytes':size(out),'exact_parent_forced_history':True})
# Already-overflowing parent is deliberately not repaired by this narrow revision.
badpair=[{'role':'assistant','content':'read'},{'role':'user','content':'中'*10000}]
out,bc,added=receipt_pressure(handed+badpair,len(handed),2)
assert out==base+badpair and size(out)>65536 and trim(out,bc)==out
results.append({'case':'inherited_parent_overflow_preserved','bytes':size(out),'not_claimed_fixed':True})
# Range coordinates remain correct after ordinary pair removal before pressure.
history=handed+[{'role':'assistant','content':'old'},{'role':'user','content':'old observation'}]+pair
bc=len(handed)
pruned=history[:bc]+history[bc+2:]
out,b,a=receipt_pressure(pruned,bc,2)
assert out==base+pair and b==len(base) and a==0
results.append({'case':'range_survives_prior_history_pruning','original_prefix_and_final_pair_preserved':True})
print(json.dumps(results))
