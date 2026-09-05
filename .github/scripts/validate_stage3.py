from pathlib import Path
import re

s = Path('sql-lab/index.html').read_text(encoding='utf-8')
required = [
    'const STAGE3_FLOW_VERSION=1;',
    'eye:"שני ענפי 1:M · קיום בלי fan-out"',
    'Raw JOIN Grain = driver × route בתוך depot',
    'function stage3RelationsHtml()',
    'function stage3PredictionWrongFeedback',
    'function stage3ExistsBridgeHtml()',
    'function stage3GuidedFlowHtml(s)',
    '∃ driver : driver.depot_id = depot.depot_id',
    'stage3SolutionExplanationHtml(choice)',
    'state.stage===3?stage3GuidedFlowHtml(s)',
    'state.stage===3&&(!stage3SanityResolved(s)||!operationChoiceResolved(s))',
]
for x in required:
    assert x in s, x

# Stage 1 and Stage 2 core content must still exist unchanged in purpose.
assert '{title:"איפה יצא כל מסלול?"' in s
assert '{title:"מי שייך לכל אתר?"' in s
assert 'function stage1CorrelatedVizHtml()' in s
assert 'function stage2CorrelatedVizHtml()' in s

scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', s)
inline = [x for x in scripts if x.strip()]
assert inline
Path('/tmp/app.js').write_text(inline[-1], encoding='utf-8')
