from pathlib import Path
import json,shutil,hashlib
p=Path(__file__).resolve().parent
w=json.loads((p/'world.json').read_text());proof=[]
def depth(node):return max([1+depth(c) for c in node.get('children',[])]+[0])
for root in ['/proc/catalog','/proc/locations']:
 oldkey=json.dumps(['Tree',{'level':0,'root':root}],sort_keys=True,separators=(',',':'))
 newkey=json.dumps(['Tree',{'level':3,'root':root}],sort_keys=True,separators=(',',':'))
 tree=w['derived_rpc'][oldkey];d=depth(tree['root']);assert d<=3
 w['derived_rpc'][newkey]=tree
 proof.append({'request':['Tree',{'root':root,'level':3}],'actual_archived_subtree_maximum_depth':d,'source_request':['Tree',{'root':'/proc','level':0}],'source_response_seq':10110,'method':'Exact archived child subtree; deepest descendant within requested limit. No nodes invented, removed or relabeled.','sha256':hashlib.sha256(json.dumps(tree,sort_keys=True).encode()).hexdigest()})
(p/'world.json').write_text(json.dumps(w,indent=2)+'\n');(p/'port-tree-derivations.json').write_text(json.dumps(proof,indent=2)+'\n')

for name in ['expected.tsv','fresh-expected.tsv','fresh-absent-inventory-expected.tsv']:
 f=p/name
 if f.exists():f.write_text(f.read_text().removesuffix('\n'))
for a,b in [('parent.py','parent.py'),('parent-readable.py','parent-readable.py'),('agent.py','candidate.py'),('readable.py','candidate-readable.py')]:shutil.copyfile(p.parent/a,p/'upstream'/b)
