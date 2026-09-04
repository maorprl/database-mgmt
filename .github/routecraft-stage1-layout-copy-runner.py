from pathlib import Path

patcher=Path('.github/routecraft-stage1-layout-copy.py')
src=patcher.read_text(encoding='utf-8')
start=src.index('# 5) Explain the relational-algebra symbols before using the expression.')
end=src.index('# Guardrails for the agreed scope.')
replacement=r'''# 5) Explain the relational-algebra symbols before using the expression.
pattern=r"function stage1JoinPredicateHtml\(\)\{\n return '<section class=\"card stage1-algebra-card\">.*?</section>';\n\}"
matches=re.findall(pattern,s,flags=re.S)
if len(matches)!=1:
    raise SystemExit(f'algebra symbol legend: expected 1 function, found {len(matches)}')
new_algebra='''function stage1JoinPredicateHtml(){
 return '<section class="card stage1-algebra-card"><div class="algebra-title">מהאלגברה הרלציונית ל-ON</div><p>לפני שקוראים את הביטוי, הנה הסימנים:</p><ul><li><b>⋈</b> = <b>Join</b> — חיבור בין שתי relations לפי תנאי התאמה.</li><li><b>σ</b> (סיגמה) = <b>Selection</b> — משאירה רק tuples שעומדים בתנאי.</li><li><b>×</b> = <b>Cartesian Product</b> — כל tuple מ-routes עם כל tuple מ-depots.</li></ul><p>לכן אפשר לחשוב על INNER JOIN כמכפלה קרטזית ואז Selection שמשאירה רק את הזוגות שעומדים ב-predicate:</p><pre>routes ⋈ depots\\n= σ_{routes.depot_id = depots.depot_id}(routes × depots)</pre><p>כאן ה-predicate הוא <span class="inline-ltr">routes.depot_id = depots.depot_id</span>. אותו תנאי נכתב ב-SQL כך:</p><pre>FROM routes r\\nINNER JOIN depots d\\n  ON r.depot_id = d.depot_id</pre><div class="algebra-principle"><b>העיקרון:</b> <span class="inline-ltr">ON r.depot_id = d.depot_id</span> הוא הדרך של SQL לכתוב את תנאי ההתאמה שקובע אילו tuples משתי ה-relations שייכים יחד.</div></section>';
}'''
s=re.sub(pattern,lambda _m:new_algebra,s,count=1,flags=re.S)

'''
modified=src[:start]+replacement+src[end:]
exec(compile(modified,str(patcher), 'exec'),{'__name__':'__main__'})
