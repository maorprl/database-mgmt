from pathlib import Path

path = Path('sql-lab/index.html')
text = path.read_text(encoding='utf-8')

old_stage = 'output:"depot_name, route_code, service_date, status, distance_km · מיון לפי route_id.",pred:'
new_stage = 'output:"depot_name, route_code, service_date, status, distance_km",sqlRequirement:"מיון לפי route_id.",pred:'
assert text.count(old_stage) == 1, f'Stage 1 output marker count: {text.count(old_stage)}'
text = text.replace(old_stage, new_stage, 1)

old_hero = '''+(s.output?('<div class="output-toggle"><button id="toggleOutput">'+(state.outputOpen[state.stage]?'הסתר דרישות פלט':'הצג דרישות פלט')+'</button></div>'+(state.outputOpen[state.stage]?'<div class="output-req"><b>דרישות פלט</b><span>'+esc(s.output)+'</span></div>':'')):'')+'</article>'+'''
new_hero = '''+(s.output?(state.stage===1?'<div class="output-req"><b>פלט מבוקש</b><span>'+esc(s.output)+'</span></div>':('<div class="output-toggle"><button id="toggleOutput">'+(state.outputOpen[state.stage]?'הסתר דרישות פלט':'הצג דרישות פלט')+'</button></div>'+(state.outputOpen[state.stage]?'<div class="output-req"><b>דרישות פלט</b><span>'+esc(s.output)+'</span></div>':''))):'')+'</article>'+'''
assert text.count(old_hero) == 1, f'Hero output marker count: {text.count(old_hero)}'
text = text.replace(old_hero, new_hero, 1)

old_editor = '''<section class="editor"><div class="editorhead"><b>'+(state.stage===1?'SQL לפתרון המשימה':'SQL editor · אתם כותבים ומריצים')+'</b><span>'+dbStatus+'</span></div><div id="cmwrap">'''
new_editor = '''<section class="editor"><div class="editorhead"><b>'+(state.stage===1?'SQL לפתרון המשימה':'SQL editor · אתם כותבים ומריצים')+'</b><span>'+((state.stage===1&&s.sqlRequirement)?'דרישת SQL: '+esc(s.sqlRequirement)+' · ':'')+dbStatus+'</span></div><div id="cmwrap">'''
assert text.count(old_editor) == 1, f'Editor header marker count: {text.count(old_editor)}'
text = text.replace(old_editor, new_editor, 1)

path.write_text(text, encoding='utf-8')
