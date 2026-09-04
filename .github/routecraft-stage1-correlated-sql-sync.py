from pathlib import Path
import re
p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

css_pat=r'''\.correlated-viz\{.*?@media\(max-width:760px\)\{\.correlated-flow\{grid-template-columns:1fr\}\.correlated-arrow\{transform:rotate\(90deg\)\}\}'''
css_new='''.correlated-viz{margin-top:12px;padding:14px;border:1px solid #d8e4dc;border-radius:12px;background:#fbfdfb}
.correlated-viz-head{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:12px}.correlated-viz-head b{font-size:12px}.correlated-viz-head span{font-size:11px;color:var(--muted);font-weight:800}
.correlated-workbench{display:grid;grid-template-columns:minmax(330px,1.05fr) minmax(300px,.95fr);gap:12px;align-items:stretch;direction:ltr}.correlated-sql-pane,.correlated-explain-pane{border:1px solid var(--line);border-radius:11px;overflow:hidden;background:#fff;min-width:0}.correlated-sql-title,.correlated-explain-title{padding:9px 11px;border-bottom:1px solid var(--line);font-size:11px;font-weight:900;color:#4d675a}.correlated-sql{padding:9px 0;background:#17251f;color:#e6eee9;direction:ltr;text-align:left;overflow:auto;min-height:290px}.correlated-sql-line{display:grid;grid-template-columns:28px minmax(max-content,1fr);gap:8px;padding:3px 12px 3px 5px;border-right:3px solid transparent;transition:.16s ease;opacity:.58}.correlated-sql-line.active{opacity:1;background:rgba(240,200,119,.16);border-right-color:#f0c877}.correlated-line-no{color:#71847a;text-align:right;user-select:none;font:11px/1.65 Consolas,monospace}.correlated-sql-line code{white-space:pre;font:12px/1.65 Consolas,monospace;color:inherit}.correlated-explain-pane{direction:rtl;text-align:right;padding-bottom:11px}.correlated-step-card{margin:11px;padding:11px 12px;border-radius:9px;background:#eef7f1;border:1px solid #cee1d5;min-height:112px}.correlated-step-card b{display:block;margin-bottom:6px;font-size:12px;color:#285e43}.correlated-step-card p{margin:0;font-size:12px;line-height:1.7;color:#405d4f}.correlated-code-link{margin:0 11px 10px;padding:8px 10px;border-radius:8px;background:#fff8ed;border:1px solid #ead8b9;color:#6f5b38;font-size:11px;line-height:1.55}.correlated-flow{display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr;gap:6px;align-items:stretch;direction:ltr;margin:0 11px}.correlated-node{border:1px solid var(--line);border-radius:9px;padding:8px;background:#fafcfb;min-width:0;transition:.16s ease;opacity:.42}.correlated-node.active{opacity:1;border-color:#7eb196;box-shadow:0 0 0 2px rgba(38,113,84,.10)}.correlated-node b{display:block;font-size:10px;margin-bottom:5px;color:#365747}.correlated-node code{display:block;white-space:normal;overflow-wrap:anywhere;font:10px/1.5 Consolas,monospace;color:var(--ink)}.correlated-arrow{display:grid;place-items:center;color:#729082;font-size:18px;font-weight:900}.correlated-controls{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:11px}.correlated-controls button{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:9px;padding:8px 12px;font-weight:800;cursor:pointer}.correlated-controls button:disabled{opacity:.35;cursor:default}.correlated-dots{display:flex;gap:5px;direction:ltr}.correlated-dot{width:7px;height:7px;border-radius:99px;background:#ccd8d1}.correlated-dot.active{background:#267154}.correlated-caption{margin-top:9px;font-size:11px;line-height:1.55;color:var(--muted)}
:root[data-theme="dark"] .correlated-viz{background:#152019;border-color:#34483d}:root[data-theme="dark"] .correlated-sql-pane,:root[data-theme="dark"] .correlated-explain-pane,:root[data-theme="dark"] .correlated-node,:root[data-theme="dark"] .correlated-controls button{background:#10241c;border-color:#46534c}:root[data-theme="dark"] .correlated-step-card{background:#173025;border-color:#365844}:root[data-theme="dark"] .correlated-step-card b{color:#bfe2ca}:root[data-theme="dark"] .correlated-step-card p{color:#cfe0d7}:root[data-theme="dark"] .correlated-code-link{background:#2b2118;border-color:#5a4222;color:#e6c79c}
@media(max-width:860px){.correlated-workbench{grid-template-columns:1fr}.correlated-sql{min-height:0}}@media(max-width:620px){.correlated-flow{grid-template-columns:1fr}.correlated-arrow{transform:rotate(90deg)}}'''
s,n=re.subn(css_pat,css_new,s,count=1,flags=re.S)
assert n==1, f'CSS patch count={n}'

fn_pat=r'''function stage1CorrelatedVizHtml\(\)\{.*?\n\}\n\nfunction sqlSupportHtml'''
fn_new=r'''function stage1CorrelatedVizHtml(){
 const total=5;
 const step=Math.max(0,Math.min(total-1,Number(((state.correlatedVizStep||{})[1])||0)));
 const titles=[
   '1 · מאיפה מתחילים?',
   '2 · מה קושר את ה-subquery ל-route הנוכחית?',
   '3 · מה ה-subquery מחזירה?',
   '4 · איפה הערך שחזר נכנס?',
   '5 · מה נשאר מה-route עצמה?'
 ];
 const texts=[
   'FROM routes r הוא ה-query החיצוני. הוא מספק את ה-routes, ולכן בכל פעם אנחנו עובדים מול route אחת. בדוגמה: route_id = 1003.',
   'WHERE d.depot_id = r.depot_id משתמש ב-r.depot_id מה-row של ה-query החיצוני. זו בדיוק הקורלציה: ה-query הפנימי תלוי ב-row החיצונית.',
   'SELECT d.depot_name FROM depots d מחפש בתוך depots ומחזיר את ה-depot_name של ה-row שהתאימה לתנאי.',
   ') AS depot_name מציב את הערך שחזר מה-subquery כ-attribute בשם depot_name בתוך אותה output row.',
   'שאר ה-attributes נלקחים ישירות מ-routes. ה-output row הושלמה, ה-Grain נשאר route, ואז ה-query החיצוני מתקדם ל-route הבאה.'
 ];
 const sqlLines=[
   'SELECT',
   '  (',
   '    SELECT d.depot_name',
   '    FROM depots d',
   '    WHERE d.depot_id = r.depot_id',
   '  ) AS depot_name,',
   '  r.route_code,',
   '  r.service_date,',
   '  r.status,',
   '  r.distance_km',
   'FROM routes r',
   'ORDER BY r.route_id;'
 ];
 const activeByStep=[[11],[5],[3,4],[6],[7,8,9,10]];
 const activeLines=new Set(activeByStep[step]);
 const sqlHtml=sqlLines.map((line,i)=>'<div class="correlated-sql-line '+(activeLines.has(i+1)?'active':'')+'"><span class="correlated-line-no">'+(i+1)+'</span><code>'+esc(line)+'</code></div>').join('');
 const nodeOn=(name)=>{
   const on={route:[0,1,4],lookup:[1,2,3],value:[3,4]}[name]||[];
   return 'correlated-node '+(on.includes(step)?'active':'');
 };
 const dots=Array.from({length:total},(_,i)=>'<span class="correlated-dot '+(i===step?'active':'')+'"></span>').join('');
 return '<div class="correlated-viz"><div class="correlated-viz-head"><b>איך השאילתה מבצעת lookup לכל route?</b><span>שלב '+(step+1)+' מתוך '+total+'</span></div>'+
   '<div class="correlated-workbench">'+
     '<div class="correlated-sql-pane"><div class="correlated-sql-title">ה-SQL · השורות הפעילות מודגשות בכל שלב</div><div class="correlated-sql">'+sqlHtml+'</div></div>'+
     '<div class="correlated-explain-pane"><div class="correlated-explain-title">מה קורה עכשיו?</div><div class="correlated-step-card"><b>'+titles[step]+'</b><p>'+texts[step]+'</p></div>'+
       '<div class="correlated-code-link">הקשר לקוד: החלק המודגש בצד שמאל הוא החלק בשאילתה שמבצע את השלב הנוכחי.</div>'+
       '<div class="correlated-flow">'+
         '<div class="'+nodeOn('route')+'"><b>route הנוכחית</b><code>route_id=1003<br>r.depot_id=2</code></div><div class="correlated-arrow">→</div>'+
         '<div class="'+nodeOn('lookup')+'"><b>lookup ב-depots</b><code>d.depot_id = r.depot_id</code></div><div class="correlated-arrow">→</div>'+
         '<div class="'+nodeOn('value')+'"><b>value שחוזר</b><code>Riverbend Crossdock</code></div>'+
       '</div></div></div>'+
   '<div class="correlated-controls"><button id="correlatedPrev" '+(step===0?'disabled':'')+'>← הקודם</button><div class="correlated-dots">'+dots+'</div><button id="correlatedNext" '+(step===total-1?'disabled':'')+'>הבא →</button></div>'+
   '<div class="correlated-caption">Correlated subquery היא query בתוך query אחר שתלויה ב-row של ה-query החיצוני. כאן היא נמצאת בתוך SELECT ומחזירה depot_name אחד לכל route.</div></div>';
}

function sqlSupportHtml'''
s,n=re.subn(fn_pat,fn_new,s,count=1,flags=re.S)
assert n==1, f'function patch count={n}'

old='''   out+='<div class="solutionbox"><div class="solution-tabs">'+options.map((x,i)=>'<button class="solution-option '+(choice===i?'active':'')+'" data-solution-choice="'+i+'">פתרון '+(i+1)+' · '+esc(x.label)+'</button>').join('')+'</div><pre>'+esc(options[choice].sql)+'</pre>';
   if(state.stage===1&&choice===1)out+=stage1CorrelatedVizHtml();'''
new='''   out+='<div class="solutionbox"><div class="solution-tabs">'+options.map((x,i)=>'<button class="solution-option '+(choice===i?'active':'')+'" data-solution-choice="'+i+'">פתרון '+(i+1)+' · '+esc(x.label)+'</button>').join('')+'</div>';
   if(state.stage===1&&choice===1)out+=stage1CorrelatedVizHtml();
   else out+='<pre>'+esc(options[choice].sql)+'</pre>';'''
assert old in s, 'solution rendering target missing'
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
