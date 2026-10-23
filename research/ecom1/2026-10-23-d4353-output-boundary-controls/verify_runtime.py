"""Verify pinned public method-only proxy implementation and native runtime version."""
import hashlib,json,platform,importlib
from importlib.metadata import version
from pathlib import Path
P=Path(__file__).resolve().parent
mod=importlib.import_module('pydantic_monty.class_instance')
a=Path(mod.__file__).read_bytes();b=(P/'runtime/class_instance.py').read_bytes()
assert a==b and version('pydantic-monty')=='1.2.0' and platform.python_version()=='3.14.3'
report={'python':'3.14.3','pydantic_monty':'1.2.0','public_class_instance_source_exact':True,'class_instance_sha256':hashlib.sha256(a).hexdigest(),'allowed_methods':['task','call','answer','llm','usage'],'lazy_attrs':'None (default)','max_feed_duration_secs':10,'max_turn_duration_secs':10,'max_suspensions':1000,'inference':'fake host only; no provider request or SDK billing semantics exercised'}
(P/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
