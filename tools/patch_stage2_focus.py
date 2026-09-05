from pathlib import Path
import re

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')
old=s

def repl(a,b,n=1):
    global s
    c=s.count(a)
    if c!=n:
        raise SystemExit(f'expected {n} occurrences, found {c}: {a[:120]!r}')
    s=s.replace(a,b,n)

repl('eye:"חיבור מידע · להעביר את העיקרון"','eye:"חיבור מידע · אותו 1:M, עכשיו NULL"')

repl('function stage2CardinalityMapHtml(){\n return \'<div class="stage1-cardinality-map"><h4>ה-Cardinality כאן</h4><div class="cardinality-line">depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;drivers</div><p><b>depots הוא צד ה-1; drivers הן צד ה-M.</b></p><p>כל driver שייכת ל-depot אחד. depot אחד יכול להיות קשור ל-0, 1 או הרבה drivers.</p></div>\';\n}\n', '''function stage2CardinalityMapHtml(){
 return '<div class="stage1-cardinality-map"><h4>ה-Cardinality כאן</h4><div class="cardinality-line">depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;drivers</div><p><b>depots הוא צד ה-1; drivers הן צד ה-M.</b></p><p>כל driver שייכת ל-depot אחד. depot אחד יכול להיות קשור ל-0, 1 או הרבה drivers.</p></div>';
}
function stage2NewFocusHtml(){
 return '<div class="stage1-concept-note"><h4>מה חדש בפרק 2?</h4><p><b>עד כאן זה אותו דפוס רלציוני של פרק 1:</b> מתחילים בצד ה-M, לכל row יש match אחד בצד ה-1, ולכן ה-Grain נשמר.</p><div class="cardinality-line">פרק 1: depots&nbsp; 1 ───── M &nbsp;routes<br>פרק 2: depots&nbsp; 1 ───── M &nbsp;drivers</div><p><b>החידוש עכשיו הוא NULL.</b> ב-drivers, ה-attribute <span class="inline-ltr">license_class</span> יכול להיות NULL. השאלה הבאה בודקת מה NULL משנה ב-row — ומה הוא לא משנה.</p></div>';
}
''')

repl('if(predQuestionResolved(2,s,3))out+=renderQ(4);','if(predQuestionResolved(2,s,3))out+=stage2NewFocusHtml()+renderQ(4);')

marker='function sqlSupportHtml(s,hintText,principleText){'
if s.count(marker)!=1:
    raise SystemExit('sqlSupport marker not unique')
stage2viz='''function stage2CorrelatedVizHtml(){
 const total=5;
 const step=Math.max(0,Math.min(total-1,Number(((state.correlatedVizStep||{})[2])||0)));
 const titles=[
   '1 · מאיפה מתחילים?',
   '2 · מה קושר את ה-subquery ל-driver הנוכחית?',
   '3 · מה ה-subquery מחזירה?',
   '4 · איפה הערך שחזר נכנס?',
   '5 · מה קורה ל-license_class?'
 ];
 const texts=[
   'FROM drivers dr הוא ה-query החיצוני. הוא מספק את ה-drivers, ולכן בכל פעם עובדים מול driver אחת.',
   'WHERE d.depot_id = dr.depot_id משתמש ב-depot_id של ה-driver הנוכחית. ה-query הפנימי תלוי ב-row של ה-query החיצוני — ולכן זו Correlated subquery.',
   'SELECT d.depot_name FROM depots d מחפש את ה-depot המתאים ומחזיר depot_name אחד. זה אפשרי כי לכל driver מתאים depot אחד בדיוק.',
   ') AS depot_name מכניס את הערך שחזר כ-attribute בתוך אותה output row של ה-driver.',
   'driver_name ו-license_class מגיעים מאותה row ב-drivers. אם license_class הוא NULL, ה-NULL נשאר בתוך ה-row; ה-driver לא נעלמת. לכן ה-Grain נשאר driver.'
 ];
 const sqlLines=[
   'SELECT',
   '  (',
   '    SELECT d.depot_name',
   '    FROM depots d',
   '    WHERE d.depot_id = dr.depot_id',
   '  ) AS depot_name,',
   '  dr.driver_name,',
   '  dr.license_class',
   'FROM drivers dr',
   'ORDER BY dr.driver_id;'
 ];
 const activeByStep=[[9],[5],[3,4],[6],[7,8]];
 const activeLines=new Set(activeByStep[step]);
 const sqlHtml=sqlLines.map((line,i)=>'<div class="correlated-sql-line '+(activeLines.has(i+1)?'active':'')+'"><span class="correlated-line-no">'+(i+1)+'</span><code>'+esc(line)+'</code></div>').join('');
 const nodeOn=(name)=>{
   const on={driver:[0,1,4],lookup:[1,2,3],value:[3,4]}[name]||[];
   return 'correlated-node '+(on.includes(step)?'active':'');
 };
 const dots=Array.from({length:total},(_,i)=>'<span class="correlated-dot '+(i===step?'active':'')+'"></span>').join('');
 return '<div class="correlated-viz"><div class="correlated-viz-head"><b>איך השאילתה מבצעת lookup לכל driver?</b><span>שלב '+(step+1)+' מתוך '+total+'</span></div>'+
   '<div class="correlated-workbench">'+
     '<div class="correlated-sql-pane"><div class="correlated-sql-title">ה-SQL · השורות הפעילות מודגשות בכל שלב</div><div class="correlated-sql">'+sqlHtml+'</div></div>'+
     '<div class="correlated-explain-pane"><div class="correlated-explain-title">מה קורה עכשיו?</div><div class="correlated-step-card"><b>'+titles[step]+'</b><p>'+texts[step]+'</p></div>'+
       '<div class="correlated-code-link">הקשר לקוד: החלק המודגש בצד שמאל הוא החלק בשאילתה שמבצע את השלב הנוכחי.</div>'+
       '<div class="correlated-flow">'+
         '<div class="'+nodeOn('driver')+'"><b>driver הנוכחית</b><code>dr.depot_id</code></div><div class="correlated-arrow">→</div>'+
         '<div class="'+nodeOn('lookup')+'"><b>lookup ב-depots</b><code>d.depot_id = dr.depot_id</code></div><div class="correlated-arrow">→</div>'+
         '<div class="'+nodeOn('value')+'"><b>value שחוזר</b><code>depot_name</code></div>'+
       '</div></div></div>'+
   '<div class="correlated-controls"><button id="correlatedPrev" '+(step===0?'disabled':'')+'>← הקודם</button><div class="correlated-dots">'+dots+'</div><button id="correlatedNext" '+(step===total-1?'disabled':'')+'>הבא →</button></div>'+
   '<div class="correlated-caption"><b>מה שונה מפרק 1?</b> מנגנון ה-lookup זהה. כאן החידוש הוא ש-NULL ב-license_class נשאר value חסר בתוך ה-driver row ואינו משנה את ה-Grain.</div></div>';
}

'''
s=s.replace(marker,stage2viz+marker,1)

repl("if(state.stage===1&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>אתגר מתקדם · לא צריך לשלוט בזה עדיין</b><p>זו דרך תקינה שמחזירה את אותה תוצאה בלי JOIN, אבל היא דורשת להבין query פנימית שתלויה ב-row של query חיצונית. פתחו אותה רק אם רוצים לראות דרך חשיבה נוספת.</p></div>'+stage1CorrelatedVizHtml();\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';", "if(state.stage===1&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>אתגר מתקדם · לא צריך לשלוט בזה עדיין</b><p>זו דרך תקינה שמחזירה את אותה תוצאה בלי JOIN, אבל היא דורשת להבין query פנימית שתלויה ב-row של query חיצונית. פתחו אותה רק אם רוצים לראות דרך חשיבה נוספת.</p></div>'+stage1CorrelatedVizHtml();\n   else if(state.stage===2&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>פתרון 2 · Correlated subquery</b><p>כאן לא מסתפקים ב-SQL עצמו: מפרקים את אותה דרך lookup שלמדנו בפרק 1, הפעם על drivers, ובודקים גם איפה NULL נכנס לתמונה.</p></div>'+stage2CorrelatedVizHtml();\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';" )

repl("if(correlatedPrev)correlatedPrev.onclick=()=>{if(!state.correlatedVizStep)state.correlatedVizStep={};state.correlatedVizStep[1]=Math.max(0,Number(state.correlatedVizStep[1]||0)-1);save();render();};\n if(correlatedNext)correlatedNext.onclick=()=>{if(!state.correlatedVizStep)state.correlatedVizStep={};state.correlatedVizStep[1]=Math.min(4,Number(state.correlatedVizStep[1]||0)+1);save();render();};", "if(correlatedPrev)correlatedPrev.onclick=()=>{if(!state.correlatedVizStep)state.correlatedVizStep={};const k=state.stage;state.correlatedVizStep[k]=Math.max(0,Number(state.correlatedVizStep[k]||0)-1);save();render();};\n if(correlatedNext)correlatedNext.onclick=()=>{if(!state.correlatedVizStep)state.correlatedVizStep={};const k=state.stage;state.correlatedVizStep[k]=Math.min(4,Number(state.correlatedVizStep[k]||0)+1);save();render();};")

if s==old:
    raise SystemExit('no changes made')
p.write_text(s,encoding='utf-8')

required=[
    'eye:"חיבור מידע · אותו 1:M, עכשיו NULL"',
    'function stage2NewFocusHtml()',
    'מה חדש בפרק 2?',
    'פרק 1: depots&nbsp; 1 ───── M &nbsp;routes',
    'פרק 2: depots&nbsp; 1 ───── M &nbsp;drivers',
    'function stage2CorrelatedVizHtml()',
    'איך השאילתה מבצעת lookup לכל driver?',
    'מה שונה מפרק 1?',
    'else if(state.stage===2&&choice===1)',
    'const k=state.stage;state.correlatedVizStep[k]'
]
for x in required:
    assert x in s, x
assert '{title:"אילו אתרים באמת פעילים?"' in s
assert 'function stage1CorrelatedVizHtml()' in s
scripts=re.findall(r'<script[^>]*>([\s\S]*?)</script>',s)
inline=[x for x in scripts if x.strip()]
Path('/tmp/app.js').write_text(inline[-1],encoding='utf-8')
