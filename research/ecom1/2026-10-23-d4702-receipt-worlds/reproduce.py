import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
D=pathlib.Path(__file__).resolve().parent
pins=json.loads((D/'SHA256SUMS.json').read_text())['files']
for name,pin in pins.items():
 b=(D/name).read_bytes();assert len(b)==pin['bytes'] and hashlib.sha256(b).hexdigest()==pin['sha256'],name
with tempfile.TemporaryDirectory(prefix='ecom1-receipt-worlds-') as tmp:
 q=pathlib.Path(tmp)/'fixture';shutil.copytree(D,q)
 subprocess.run([sys.executable,str(q/'prepare.py')],check=True,stdout=subprocess.DEVNULL)
 for name in pins:
  assert (q/name).read_bytes()==(D/name).read_bytes(),name
print(json.dumps({'status':'PASS','sealed_files_verified':len(pins),'all_reconstructed_outputs_identical':True}))
