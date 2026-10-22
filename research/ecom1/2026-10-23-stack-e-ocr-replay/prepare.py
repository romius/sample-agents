"""Prepare immutable archived-world maps and a separately transcribed TSV oracle."""
import copy,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def sha(x):return hashlib.sha256(x).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
requests={e['seq']:e for e in map(json.loads,(P/'events-t076.jsonl').read_text().splitlines())}
responses=sorted([e for f in ['initial-rpc-responses.jsonl','remaining-rpc-responses.jsonl'] for e in map(json.loads,(P/f).read_text().splitlines())],key=lambda x:x['seq'])
index=json.loads((P/'index-t076.json').read_text())
assert {e['seq'] for e in responses}=={e[0] for e in index if e[1]=='rpc_response'}
raw={e['seq']:l for f in ['initial-rpc-responses.jsonl','remaining-rpc-responses.jsonl'] for l in (P/f).read_text().splitlines(keepends=True) for e in [json.loads(l)]}
for seq,kind,method,n in index:
 if kind=='rpc_response':assert len(raw[seq].encode())==n,(seq,n)
rpc={};files={};lineage=[]
for e in responses:
 q=requests[e['seq']-1]['data'];d=e['data'];assert q['method']==d['method'];r=d['response'];key=canon([q['method'],q['arguments']])
 if key in rpc:assert rpc[key]==r
 rpc[key]=r
 if d['method']=='Read':
  assert sha(r['content'].encode())==r['sha256']
  if r['path'] in files:assert files[r['path']]==r
  files[r['path']]=r
 lineage.append({'request_seq':e['seq']-1,'response_seq':e['seq'],'method':d['method'],'arguments':q['arguments'],'raw_response_sha256':sha(raw[e['seq']].encode()),'raw_bytes':len(raw[e['seq']].encode())})
task=next(e['data']['response'] for e in responses if e['data']['method']=='StartTrial')
tree=next(e['data']['response'] for e in responses if e['seq']==10110)
assert requests[10109]['data']['arguments']=={'root':'/proc','level':0}
assert not any(tree.get(k) for k in ['truncated','more','next','next_cursor'])
derived={};derivations=[]
for root in ['/proc/catalog','/proc/locations']:
 node=next(n for n in tree['root']['children'] if n['name']==root.split('/')[-1]);assert node['kind']=='NODE_KIND_DIR'
 paths=[]
 def walk(n,p):
  if n['kind']=='NODE_KIND_DIR':
   assert 'children' in n,n
   for ch in n['children']:walk(ch,p+'/'+ch['name'])
  else:paths.append(p)
 walk(node,root)
 assert all(p in files for p in paths),[p for p in paths if p not in files]
 derived[canon(['Tree',{'root':root,'level':0}])]={'root':copy.deepcopy(node)}
 derivations.append({'derived_request':['Tree',{'root':root,'level':0}],'source_response_seq':10110,'source_request':requests[10109]['data']['arguments'],'method':'Select exact child subtree by directory name; preserve all node fields and descendants. No entries added.','leaves':len(paths),'all_leaves_have_actual_read_responses':True,'paths':paths})
router=next(e['data']['response'] for e in requests.values() if e['seq']==10092)
upload='/uploads/5qt53BQ6_competitor_purchase_request_ocr.txt'
world={'task':task,'rpc':rpc,'files':files,'derived_rpc':derived,'router_response':router,'upload':upload,'export':'/exports/crosslist-JgSownP1.tsv'}
save('world.json',world);save('world-provenance.json',{'job':'j55b49f183413406c850865f5aa62012b','trial_id':task['trialId'],'trace_blob':'dcd9333354fb1c5c72b39dc2e6c24dc5ffacbb2d70004ec9c384f26540b118fc','all_rpc_responses':len(responses),'rpc_response_bytes':sum(len(v.encode()) for v in raw.values()),'distinct_read_files':len(files),'lineage':lineage,'derived_trees':derivations,'limit':'Complete archived Tree response and corresponding leaf Reads demonstrate covered catalogue/store leaves; no independent current-server completeness promise is inferred.'})
# Manual transcription from actual OCR, intentionally independent of candidate parsing.
manual=[
 [1,'CMP-E2YTNR',9,'Einhell TE-AC 270/50 Silent Plus compressor',{'noise_db':88,'oil_free':False,'tank_l':50}],
 [2,'CMP-4ZDNFH',8,'Karcher K4 Power Control Car and Home set',{'accessory_set':'car and home kit','detergent_system':'plug and clean','flow_l_h':410,'pump_material':'aluminium'}],
 [3,'CMP-JWCCAD',6,'3M SecureFit 400 clear safety glasses with foam gasket',{'adjustable':False,'certification':'EN166','pack_count':1}],
 [4,'CMP-32UKXC',4,'Aircraft Compact-Air 240/24 compressor accessory set',{'intake_l_min':240,'noise_db':97,'wheels':True}],
 [5,'CMP-HKAPN2',9,'Uvex Pheos helmet visor kit',{'pack_count':1,'protection_type':'face','size':'helmet mounted'}]]
assert sum(x[2] for x in manual)==36
products=[json.loads(r['content']) for p,r in files.items() if p.startswith('/proc/catalog/')]
store=json.loads(files['/proc/locations/Graz/store-graz-center.json']['content'])
header='line_no competitor_code requested_description requested_qty branch_id branch_open match_status matched_sku matched_product_name available_today fulfillable_qty short_qty reason'.split()
oracle=[]
for line,code,qty,name,properties in manual:
 matches=[p for p in products if p['name'].casefold()==name.casefold()];assert len(matches)==1;p=matches[0]
 exact=all(type(p['properties'].get(k)) is type(v) and p['properties'].get(k)==v for k,v in properties.items())
 rows=[r for r in store['inventory'] if r['sku']==p['sku']];assert len(rows)==1 if exact else len(rows)<=1;r=rows[0] if rows else {}
 avail=max(r.get('on_hand',0)-r.get('reserved',0),0) if exact else 0
 fulfill=min(qty,avail) if exact and store['is_open'] else 0
 reason=('requested properties do not exactly match catalogue product' if not exact else 'target branch is closed today' if not store['is_open'] else 'exact property match; requested quantity available today' if fulfill==qty else 'exact property match; branch has insufficient same-day stock')
 oracle.append([line,code,p['name'],qty,store['id'],str(store['is_open']).lower(),'exact' if exact else 'property_mismatch',p['sku'] if exact else '',p['name'] if exact else '',avail,fulfill,qty-fulfill,reason])
tsv='\t'.join(header)+'\n'+''.join('\t'.join(map(str,r))+'\n' for r in oracle)
(P/'expected.tsv').write_text(tsv)
save('manual-oracle.json',{'ocr_response_seq':10098,'ocr_sha256':files[upload]['sha256'],'policy_response_seq':10094,'branch':store['name'],'manual_ocr_rows':manual,'columns':header,'expected_rows':oracle,'expected_tsv_sha256':sha(tsv.encode()),'independence':'No candidate parser/render/stock helper used. Exact manually typed properties compared with complete actual catalogue JSONs and actual branch inventory; row2 flow410 conflicts with420.'})
fresh_ocr='PowerTools target branch: PowerTools Graz Center\nLine Qty Competitor Requested item / properties\n1 2 NEW-BODY Bosch Professional GSR 18V-55 cordless drill body\nspecs: chuck mm=13; power source=cordless; brushless=true; kit=body only\n2 3 NEW-KIT Bosch Professional GSR 18V-55 drill kit 2x2.0Ah\nspecs: chuck mm=13; power source=cordless; kit=2x2.0Ah batteries and charger\nTotal requested lines: 2\nTotal requested units: 5\n'
fresh_manual=[(1,'NEW-BODY',2,'PT-DRL-BOS-GSR55-BODY',{'chuck_mm':13,'power_source':'cordless','brushless':True,'kit':'body only'}),
 (2,'NEW-KIT',3,'PT-DRL-BOS-GSR55-2AH',{'chuck_mm':13,'power_source':'cordless','kit':'2x2.0Ah batteries and charger'})]
fresh_rows=[]
for line,code,qty,sku,properties in fresh_manual:
 p=next(p for p in products if p['sku']==sku)
 assert all(p['properties'][k]==v and type(p['properties'][k]) is type(v) for k,v in properties.items())
 rr=[r for r in store['inventory'] if r['sku']==sku];assert len(rr)==1;r=rr[0]
 avail=max(r.get('on_hand',0)-r.get('reserved',0),0);fulfill=min(qty,avail)
 reason='exact property match; requested quantity available today' if fulfill==qty else 'exact property match; branch has insufficient same-day stock'
 fresh_rows.append([line,code,p['name'],qty,store['id'],'true','exact',sku,p['name'],avail,fulfill,qty-fulfill,reason])
fresh_tsv='\t'.join(header)+'\n'+''.join('\t'.join(map(str,r))+'\n' for r in fresh_rows)
(P/'fresh-two-row-ocr.txt').write_text(fresh_ocr);(P/'fresh-expected.tsv').write_text(fresh_tsv)
save('fresh-manual-oracle.json',{'provenance':'Synthetic new two-row purchase request using different actual archived catalogue families and branch stock. Not an actual user/provider request.','manual_rows':fresh_manual,'expected_rows':fresh_rows,'ocr_sha256':sha(fresh_ocr.encode()),'tsv_sha256':sha(fresh_tsv.encode())})
print(json.dumps({'rpc_responses':len(responses),'files':len(files),'derived_trees':[(x['derived_request'][1]['root'],x['leaves']) for x in derivations],'oracle_rows':len(oracle),'oracle_sha':sha(tsv.encode())}))
