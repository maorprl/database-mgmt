from pathlib import Path
import re

script_path = Path('.github/routecraft-stage1-pedagogy-polish.py')
src = script_path.read_text(encoding='utf-8')

# The main patch script's last exact-string replacement was too strict for the render line.
# Run all preceding narrow patches, skip only that replacement, then patch the render line by regex.
src = re.sub(
    r"# Stage 1 final result uses the measured baseline instead of repeating generic prose\.[\s\S]*?(?=# Guardrails:)",
    "",
    src,
    count=1,
)
ctx = {'__name__': '__main__'}
exec(compile(src, str(script_path), 'exec'), ctx)

path = Path('sql-lab/index.html')
s = path.read_text(encoding='utf-8')

# Keep line breaks inside the generated JS string escaped rather than literal.
algebra_old = "routes ⋈ depots\n= σ_{routes.depot_id = depots.depot_id}(routes × depots)"
algebra_new = "routes ⋈ depots\\n= σ_{routes.depot_id = depots.depot_id}(routes × depots)"
sql_old = "FROM routes r\nINNER JOIN depots d\n  ON r.depot_id = d.depot_id"
sql_new = "FROM routes r\\nINNER JOIN depots d\\n  ON r.depot_id = d.depot_id"
if s.count(algebra_old) != 1:
    raise SystemExit(f'algebra multiline escape: expected 1 match, found {s.count(algebra_old)}')
if s.count(sql_old) != 1:
    raise SystemExit(f'ON multiline escape: expected 1 match, found {s.count(sql_old)}')
s = s.replace(algebra_old, algebra_new, 1).replace(sql_old, sql_new, 1)

pattern = re.compile(
    r"\+\(lastResult&&s\.sanity\?'<div class=\"result-verify\"><b>Verify:</b> '\+mixedInlineHtml\(s\.sanity\.after\)\+'</div>':''\)\+"
)
replacement = "+(lastResult&&s.sanity?(state.stage===1?stage1FinalSanityHtml(s):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')+"
s, n = pattern.subn(lambda m: replacement, s, count=1)
if n != 1:
    raise SystemExit(f'stage1 final sanity compare regex: expected 1 match, found {n}')
path.write_text(s, encoding='utf-8')
print('patched final Stage 1 sanity compare and algebra line escapes')
