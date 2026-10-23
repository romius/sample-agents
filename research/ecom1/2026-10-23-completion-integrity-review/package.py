"""Build a deterministic, lossless archive without generated publication files."""
from pathlib import Path
import hashlib, io, json, lzma, tarfile

P = Path(__file__).resolve().parent
files = sorted(p for p in P.rglob('*') if p.is_file()
               and '__pycache__' not in p.parts
               and 'publication' not in p.relative_to(P).parts)
out = P / 'publication'
out.mkdir(exist_ok=True)
target = out / 'evidence.tar.xz'
with lzma.open(target, 'wb', preset=6) as compressed:
    with tarfile.open(fileobj=compressed, mode='w|') as archive:
        for path in files:
            data = path.read_bytes()
            info = tarfile.TarInfo(str(path.relative_to(P)))
            info.size = len(data)
            info.mode = 0o644
            archive.addfile(info, io.BytesIO(data))
data = target.read_bytes()
meta = {'members': len(files), 'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest()}
(out / 'archive.json').write_text(json.dumps(meta, indent=2) + '\n')
print(json.dumps(meta))
