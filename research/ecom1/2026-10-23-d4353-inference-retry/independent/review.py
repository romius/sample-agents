"""Independent boundary counterexamples; offline public Monty host only."""
import copy, hashlib, json, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P))
import pydantic_monty as monty
from host import Host, W, execute, response

class BoundaryHost(Host):
    def llm(self, *args, **kwargs):
        result = super().llm(*args, **kwargs)
        if kwargs.get('max_completion_tokens') != 1024 and self.case.get('bad_response'):
            return {'choices': []}
        return result

cases = [dict(name='successful_transport_invalid_structure', bad_response=True)]
for tool in ('write', 'delete', 'exec'):
    action = {'tool': tool, 'path': W['export']}
    if tool == 'write': action['content'] = 'independent scripted mutation'
    if tool == 'exec': action.update(path='/bin/discount', args=['SCRIPTED'], stdin='')
    for error in ('HTTP 503 unavailable', 'Inference outcome/cost unconfirmed: TimeoutError: The read operation timed out'):
        cases.append(dict(name=tool+'_'+str(len(cases)), write_first=True,
                          first_action=action, mutation_error=error))
rows = []
with monty.Monty() as pool:
    for version in ('parent', 'sdk-only', 'guest-owned'):
        for form in ('readable', 'packed'):
            path = P/('parent-readable.py' if form == 'readable' else 'parent.py') if version == 'parent' else P/version/('readable.py' if form == 'readable' else 'agent.py')
            for case in cases:
                row = execute(pool, path.read_text(), copy.deepcopy(case), BoundaryHost)
                assert row['raised'] and not row['answers'], (version, form, case, row)
                assert row['llm_stages'] == {'router': 1, 'main': 1}, row
                assert len(row['mutations']) == (0 if case.get('bad_response') else 1), row
                row.update(version=version, form=form)
                rows.append(row)
pins = json.loads((P/'SHA256SUMS.json').read_text())
for name, pin in pins.items():
    data = (P/name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == pin['sha256'], name
    assert len(data) == pin['bytes'], name
report = {'status': 'PASS', 'independent_whole_agent_checks': len(rows),
          'sealed_files_unchanged': len(pins), 'no_network_or_model_calls': True,
          'findings': 'Successful transport with invalid response structure is not retried. Mutation errors containing precisely retryable inference text remain outside the retry boundary and execute once.',
          'results': rows}
(P/'independent/boundary-results.json').write_text(json.dumps(report, indent=2)+'\n')
print('PASS', len(rows), 'independent boundary checks;', len(pins), 'sealed files unchanged')
