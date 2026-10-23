"""Prepare empty review coverage ledger. It contains no output judgments."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;plan=json.loads((P/'inputs/call-plan.json').read_text())
rows=[]
for cell in plan['calls']:
 rows.append({**cell,'group':'equal-input variation control' if cell['fixture']=='V016' else 'primary effort comparison','boundary_fixture':'A016' if cell['fixture']=='V016' else cell['fixture'],'review_state':'UNOBSERVED','opaque_review_id':None,'immutable_response_event':None,'response_sha256':None,'finish_reason':None,'final_presence':None,'strict_schema':None,'source_parser':None,'main_length_suppression':None,'manual_action_support':None,'unsupported_assertions':None,'qualifiers':None,'proposed_mutation':None,'completion_claims_and_acknowledgements':None,'refs':None,'visible_evidence_citations':None,'uncertainty':None,'reviewer':None,'independent_review':None,'disagreement':None})
(P/'review-coverage-template.json').write_text(json.dumps({'notice':'Coverage ledger only. Do not expose fixture/arm mapping in partially blinded first-review inputs. No outputs collected or evaluated.','rows':rows},indent=2)+'\n')
