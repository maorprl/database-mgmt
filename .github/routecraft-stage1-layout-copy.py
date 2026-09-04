from pathlib import Path
import re

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

def repl(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s=s.replace(old,new,1)

def repl_first(old,new,label):
    global s
    n=s.count(old)
    if n<1:
        raise SystemExit(f'{label}: expected at least 1 match, found 0')
    s=s.replace(old,new,1)

# 1) Make the Stage 1 Cardinality answer explicit about the direction and make Q4 tie back to it.
repl(
'''why:"Cardinality מתארת כמה rows מצד אחד יכולות להיות קשורות ל-row אחת מהצד השני, ובודקים כל כיוון בנפרד. כאן לכל route יש depot_id שחייב להתאים ל-depot_id שקיים ב-depots. מכיוון ש-depots.depot_id הוא Primary Key, לכל route מתאים depot אחד בדיוק. בכיוון ההפוך, depot אחד יכול להיות קשור ל-0, 1 או הרבה routes.",concept:"Cardinality: depots 1 → M routes — depot אחד יכול להיות קשור ל-routes רבות; כל route שייכת ל-depot אחד."},{q:"אם לכל route מתאים depot אחד בדיוק, מה יקרה אחרי החיבור?",opts:[["same","כל route תישאר שורה אחת"],["multiply","routes יוכפלו"],["drop","חלק מה-routes ייעלמו"],["aggregate","כמה routes יאוחדו לשורה אחת"]],ans:"same",why:"לכל route מצטרף depot אחד בלבד, ולכן כל route נשארת שורה אחת גם אחרי החיבור. ה-Grain נשאר route."}''',
'''why:"לכל route יש depot_id שחייב להתאים ל-depot_id שקיים ב-depots. מכיוון ש-depots.depot_id הוא Primary Key, לכל route מתאים depot אחד בדיוק. בכיוון ההפוך, depot אחד יכול להיות קשור ל-0, 1 או הרבה routes.",concept:"Cardinality = כמה rows יכולות להיות קשורות בכל כיוון. כאן: depots 1:M routes."},{q:"אם לכל route מתאים depot אחד בדיוק, מה יקרה אחרי החיבור?",opts:[["same","כל route תישאר שורה אחת"],["multiply","routes יוכפלו"],["drop","חלק מה-routes ייעלמו"],["aggregate","כמה routes יאוחדו לשורה אחת"]],ans:"same",why:"אנחנו מתחילים מ-routes, צד ה-M בקשר. מאחר שלכל route יש depot אחד בדיוק בצד ה-1, כל route מקבלת match יחיד ולא מתפצלת לכמה rows. לכן ה-Grain נשאר route ומספר ה-rows נשמר."}''',
'cardinality/q4 copy')

# 2) Improve the PK/FK bridge and add one-time Cardinality explanation + explicit 1:M map.
repl(
'''function stage1KeyGuideHtml(){
 return '<div class="stage1-key-guide"><h4>איך קוראים את הסימון?</h4><div class="key-link">routes.depot_id → depots.depot_id</div><ul><li><b>PK</b> מזהה row אחת באופן ייחודי.</li><li><b>FK</b> הוא attribute שמצביע ל-key ב-relation אחרת.</li><li><b>NOT NULL</b> אומר שחייב להיות ערך ב-attribute הזה.</li></ul></div>';
}''',
'''function stage1KeyGuideHtml(){
 return '<div class="stage1-key-guide"><h4>איך routes ו-depots קשורות?</h4><div class="key-link">routes.depot_id (FK) → depots.depot_id (PK)</div><ul><li><b>PK</b> מזהה row אחת באופן ייחודי.</li><li><b>FK</b> אומר שהערך ב-routes.depot_id חייב להתאים ל-depot_id שקיים ב-depots.</li><li><b>NOT NULL</b> אומר שלכל route חייב להיות depot_id.</li></ul><p class="key-arrow-note">החץ כאן מציג את קשר ה-FK בין ה-relations. הוא לא מתאר את ה-Cardinality.</p></div>';
}
function stage1CardinalityIntroHtml(){
 return '<div class="stage1-concept-note"><h4>מה זה Cardinality?</h4><p>Cardinality מתארת <b>כמה rows מצד אחד יכולות להיות קשורות ל-row אחת מהצד השני</b>.</p><p>בודקים את הקשר בכל כיוון בנפרד. עכשיו נבדוק: ל-route אחת, כמה depots יכולים להתאים?</p></div>';
}
function stage1CardinalityMapHtml(){
 return '<div class="stage1-cardinality-map"><h4>ה-Cardinality כאן</h4><div class="cardinality-line">depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;routes</div><p><b>depots הוא צד ה-1; routes הן צד ה-M.</b></p><p>כל route שייכת ל-depot אחד. depot אחד יכול להיות קשור ל-0, 1 או הרבה routes.</p></div>';
}''',
'key guide/cardinality helpers')

# 3) Put the relevant relations under Question 2's wording, before its answer control.
repl(
'''const renderQ=(qi)=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(1,qi);''',
'''const renderQ=(qi,afterLabel='')=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(1,qi);''',
'renderQ signature')
repl_first(
'''return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label><select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';''',
'''return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label>'+afterLabel+'<select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';''',
'renderQ body')
repl(
'''let out=renderQ(0);
   if(predQuestionResolved(1,s,0))out+=stage1RelationsHtml()+renderQ(1);
   if(predQuestionResolved(1,s,1))out+=stage1KeyGuideHtml()+renderQ(2);
   if(predQuestionResolved(1,s,2))out+=renderQ(3);''',
'''let out=renderQ(0);
   if(predQuestionResolved(1,s,0))out+=renderQ(1,stage1RelationsHtml());
   if(predQuestionResolved(1,s,1))out+=stage1KeyGuideHtml()+stage1CardinalityIntroHtml()+renderQ(2);
   if(predQuestionResolved(1,s,2))out+=stage1CardinalityMapHtml()+renderQ(3);''',
'stage1 question flow')

# 4) Add minimal styling for the explanatory blocks, without changing the rest of the UI.
repl(
'''.stage1-key-guide ul{margin:0;padding-right:18px}.stage1-key-guide li{margin:3px 0}:root[data-theme="dark"] .stage1-business-anchor{background:#2a211a}:root[data-theme="dark"] .stage1-relation,:root[data-theme="dark"] .stage1-key-guide{background:#152019}:root[data-theme="dark"] .stage1-relation h4{background:#1a2820}@media(max-width:760px){.stage1-relations{grid-template-columns:1fr}}''',
'''.stage1-key-guide ul{margin:0;padding-right:18px}.stage1-key-guide li{margin:3px 0}.stage1-key-guide .key-arrow-note{margin:8px 0 0;color:var(--muted)}.stage1-concept-note,.stage1-cardinality-map{margin:12px 0;padding:12px 14px;border:1px solid #d8e2dc;border-radius:10px;background:#f7faf8;font-size:12px;line-height:1.65}.stage1-concept-note h4,.stage1-cardinality-map h4{margin:0 0 7px;font-size:12px}.stage1-concept-note p,.stage1-cardinality-map p{margin:5px 0}.stage1-cardinality-map .cardinality-line{direction:ltr;text-align:center;font:900 14px Consolas,monospace;padding:8px 0}:root[data-theme="dark"] .stage1-business-anchor{background:#2a211a}:root[data-theme="dark"] .stage1-relation,:root[data-theme="dark"] .stage1-key-guide,:root[data-theme="dark"] .stage1-concept-note,:root[data-theme="dark"] .stage1-cardinality-map{background:#152019}:root[data-theme="dark"] .stage1-relation h4{background:#1a2820}@media(max-width:760px){.stage1-relations{grid-template-columns:1fr}}''',
'stage1 helper styles')

# 5) Explain the relational-algebra symbols before using the expression.
repl(
'''function stage1JoinPredicateHtml(){
 return '<section class="card stage1-algebra-card"><div class="algebra-title">מהאלגברה הרלציונית ל-ON</div><p>אפשר לחשוב על INNER JOIN כמכפלה קרטזית ואז Selection לפי predicate שמחליט אילו זוגות נשארים:</p><pre>routes ⋈ depots\\
= σ_{routes.depot_id = depots.depot_id}(routes × depots)</pre><p>אותו predicate נכתב ב-SQL כך:</p><pre>FROM routes r\\
INNER JOIN depots d\\
  ON r.depot_id = d.depot_id</pre><div class="algebra-principle"><b>העיקרון:</b> <span class="inline-ltr">ON r.depot_id = d.depot_id</span> הוא ה-predicate שקובע אילו tuples משתי ה-relations הם matches.</div></section>';
}''',
'''function stage1JoinPredicateHtml(){
 return '<section class="card stage1-algebra-card"><div class="algebra-title">מהאלגברה הרלציונית ל-ON</div><p>לפני שקוראים את הביטוי, הנה הסימנים:</p><ul><li><b>⋈</b> = <b>Join</b> — חיבור בין שתי relations לפי תנאי התאמה.</li><li><b>σ</b> (סיגמה) = <b>Selection</b> — משאירה רק tuples שעומדים בתנאי.</li><li><b>×</b> = <b>Cartesian Product</b> — כל tuple מ-routes עם כל tuple מ-depots.</li></ul><p>לכן אפשר לחשוב על INNER JOIN כמכפלה קרטזית ואז Selection שמשאירה רק את הזוגות שעומדים ב-predicate:</p><pre>routes ⋈ depots\\
= σ_{routes.depot_id = depots.depot_id}(routes × depots)</pre><p>כאן ה-predicate הוא <span class="inline-ltr">routes.depot_id = depots.depot_id</span>. אותו תנאי נכתב ב-SQL כך:</p><pre>FROM routes r\\
INNER JOIN depots d\\
  ON r.depot_id = d.depot_id</pre><div class="algebra-principle"><b>העיקרון:</b> <span class="inline-ltr">ON r.depot_id = d.depot_id</span> הוא הדרך של SQL לכתוב את תנאי ההתאמה שקובע אילו tuples משתי ה-relations שייכים יחד.</div></section>';
}''',
'algebra symbol legend')

# Guardrails for the agreed scope.
required=[
    'renderQ(1,stage1RelationsHtml())',
    'איך routes ו-depots קשורות?',
    'החץ כאן מציג את קשר ה-FK בין ה-relations. הוא לא מתאר את ה-Cardinality.',
    'מה זה Cardinality?',
    'depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;routes',
    'depots הוא צד ה-1; routes הן צד ה-M.',
    'צד ה-M בקשר',
    'σ</b> (סיגמה) = <b>Selection</b>',
    '×</b> = <b>Cartesian Product</b>'
]
for text in required:
    if text not in s:
        raise SystemExit(f'missing required text: {text}')

p.write_text(s,encoding='utf-8')
print('patched', p)
