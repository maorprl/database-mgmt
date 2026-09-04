from pathlib import Path
import re

path = Path('sql-lab/index.html')
s = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s.replace(old, new, 1)

# 1) Narrow Stage 1 styles: measured sanity, algebra bridge, advanced challenge.
css_anchor = ".solution-option.active{background:#eaf5ef;border-color:#a9cdb7;color:#285e43}\n.solution-note{font-size:12px;color:var(--muted);line-height:1.65}\n"
css_new = ".solution-option.active{background:#eaf5ef;border-color:#a9cdb7;color:#285e43}\n.solution-option.advanced{margin-inline-start:10px;border-style:dashed;border-color:#c79a58;background:#fffaf0;color:#765c32}\n.advanced-solution-intro{margin:10px 0 12px;padding:11px 12px;border:1px solid #ead8aa;border-radius:10px;background:#fffaf0;color:#6f5b38;font-size:12px;line-height:1.65}\n.advanced-solution-intro b{display:block;margin-bottom:4px}\n.advanced-solution-intro p{margin:0}\n.stage1-algebra-card{padding:17px 19px;border-right:4px solid #6c78a8}\n.stage1-algebra-card .algebra-title{font-size:12px;font-weight:900;color:#45548c;margin-bottom:8px}\n.stage1-algebra-card p{margin:7px 0;color:var(--muted);font-size:12px;line-height:1.7}\n.stage1-algebra-card pre{direction:ltr;text-align:left;white-space:pre-wrap;margin:10px 0;background:#17251f;color:#e6eee9;padding:12px;border-radius:9px;overflow:auto;font:12px/1.65 Consolas,monospace}\n.stage1-algebra-card .algebra-principle{margin-top:10px;padding:9px 11px;border-radius:9px;background:#eef5f9;border:1px solid #cfdee8;color:#34556e}\n.stage1-baseline-check .baseline-number{display:inline-block;direction:ltr;unicode-bidi:isolate;font-family:Consolas,monospace;font-weight:900;color:#285e43}\n.result-verify.stage1-sanity-pass{background:#edf8f1;color:#285e43}\n.result-verify.stage1-sanity-warn{background:#fff5f1;color:#864b38}\n.solution-note{font-size:12px;color:var(--muted);line-height:1.65}\n"
replace_once(css_anchor, css_new, 'stage1 styles')

css_dark_anchor = ":root[data-theme=\"dark\"] .operation-help .op-tool,:root[data-theme=\"dark\"] .solution-option.active{background:#173025;border-color:#365844;color:#bfe2ca}\n"
css_dark_new = ":root[data-theme=\"dark\"] .operation-help .op-tool,:root[data-theme=\"dark\"] .solution-option.active{background:#173025;border-color:#365844;color:#bfe2ca}\n:root[data-theme=\"dark\"] .solution-option.advanced,:root[data-theme=\"dark\"] .advanced-solution-intro{background:#2b2418;border-color:#5a4930;color:#e6c79c}\n:root[data-theme=\"dark\"] .stage1-algebra-card .algebra-principle{background:#172934;border-color:#365367;color:#b9d7e9}\n"
replace_once(css_dark_anchor, css_dark_new, 'stage1 dark styles')

# 2) Stage 1 wrong-answer feedback is specific to the selected mistake.
pred_anchor = "function predictionQuizHtml(s){\n"
pred_helper = """function stage1PredictionWrongFeedback(qi,choice){
 const hints={
   0:{
     depot:'הבקשה היא רשימה של מסלולים. שאלו את עצמכם מה אמור להופיע פעם אחת בכל row — האתר או המסלול?',
     vehicle:'vehicle הוא פרט שיכול להיות קשור למסלול, אבל הוא לא יחידת הרשימה שהבקשה מבקשת.',
     stop:'stop היא רמה מפורטת יותר מהבקשה. כאן לא מבקשים row לכל עצירה.'
   },
   1:{
     route_code:'בדקו שוב את schema של routes: route_code כבר נמצא שם. חפשו attribute שהבקשה דורשת ואינו ב-routes.',
     service_date:'service_date כבר נמצא ב-routes. חפשו את הפריט שחייב להגיע מ-relation אחרת.',
     distance_km:'distance_km כבר נמצא ב-routes. איזה attribute נדרש בפלט אך נמצא רק ב-depots?'
   },
   2:{
     zero:'routes.depot_id הוא FK וגם NOT NULL. מה שני האילוצים האלה אומרים לגבי האפשרות שלא יהיה match?',
     many:'הסתכלו על depots.depot_id: הוא Primary Key. האם אותו depot_id יכול לזהות כמה rows ב-depots?',
     unknown:'ה-schema כן נותן מספיק מידע: PK קובע ייחודיות, ו-FK + NOT NULL קובעים שהפניה חייבת להתאים.'
   },
   3:{
     multiply:'כדי ש-route תתפצל לכמה rows צריך כמה matches ב-depots. חזרו ל-cardinality שקבעתם עכשיו.',
     drop:'INNER JOIN יכול להוריד unmatched rows באופן כללי, אבל כאן FK + NOT NULL מבטיחים שלכל route יש depot תואם.',
     aggregate:'אין כאן סיכום של כמה routes ל-row אחת; אנחנו רק מוסיפים attribute מה-depot ל-route הקיימת.'
   }
 };
 return (hints[qi]&&hints[qi][choice])||'חזרו ל-Grain, ל-schema ולקשר בין ה-relations.';
}

function predictionQuizHtml(s){
"""
replace_once(pred_anchor, pred_helper, 'prediction helper')

pred_exp_old = "     const exp=(checked&&cur)?('<div class=\"answer-exp '+(cur===q.ans?'good':'wrong')+'\"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(q.why)+concept+'</div>'):'';\n"
pred_exp_new = "     const answerText=cur===q.ans?q.why:stage1PredictionWrongFeedback(qi,cur);\n     const exp=(checked&&cur)?('<div class=\"answer-exp '+(cur===q.ans?'good':'wrong')+'\"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(answerText)+concept+'</div>'):'';\n"
replace_once(pred_exp_old, pred_exp_new, 'stage1 prediction feedback')

# 3) Wrong operation choices explain why that operator does not fit this request.
op_anchor = "function operationHtml(s){\n"
op_helper = """function stage1OperationWrongFeedback(choice){
 if(choice==='exists')return 'EXISTS עונה על שאלת קיום. כאן צריך להביא את depot_name עצמו אל ה-output row, לא רק לבדוק אם depot קיים.';
 if(choice==='left')return 'LEFT OUTER JOIN נועד לשמור rows גם כשאין match. כאן ה-FK ו-NOT NULL מבטיחים שלכל route יש depot תואם, ולכן אין unmatched route שצריך לשמר.';
 if(choice==='group')return 'GROUP BY משנה את רמת הפירוט ומסכם כמה rows. כאן ה-Grain כבר route ואנחנו רק מוסיפים attribute אחד מה-depot.';
 return 'חזרו ל-Grain ולתפקיד של depots: צריך attribute מה-row התואמת, לא בדיקת קיום ולא aggregation.';
}

function operationHtml(s){
"""
replace_once(op_anchor, op_helper, 'operation helper')

op_wrong_old = "   else if(checked)body+='<div class=\"op-feedback bad\"><b>עוד לא.</b> חזרו ל-Grain ולתפקיד של כל relation.</div>';\n"
op_wrong_new = "   else if(checked)body+='<div class=\"op-feedback bad\"><b>עוד לא.</b> '+esc(state.stage===1?stage1OperationWrongFeedback(cur):'חזרו ל-Grain ולתפקיד של כל relation.')+'</div>';\n"
replace_once(op_wrong_old, op_wrong_new, 'operation wrong feedback')

# 4) Stage 1 Sanity Check becomes a measured baseline, not another choice question.
sanity_resolved_old = "function stage1SanityResolved(s){\n return state.stage===1&&!!(s.sanity&&state.sanityChecked[1]&&state.sanityAnswers[1]===s.sanity.ans);\n}\n"
sanity_resolved_new = "function stage1SanityResolved(s){\n return state.stage===1&&!!((state.exploreRan||{})[1]);\n}\n"
replace_once(sanity_resolved_old, sanity_resolved_new, 'stage1 sanity resolved')

explore_anchor = "function stage1ExplorationHtml(s){\n"
explore_helpers = """function stage1BaselineCount(s){
 const saved=Number((state.stage1BaselineCount===undefined||state.stage1BaselineCount===null)?NaN:state.stage1BaselineCount);
 if(Number.isFinite(saved))return saved;
 if(!((state.exploreRan||{})[1])||!db||!s.sanity||!s.sanity.baselineSql)return null;
 try{
   const r=exec(s.sanity.baselineSql);
   const n=Number(r&&r.values&&r.values[0]&&r.values[0][0]);
   return Number.isFinite(n)?n:null;
 }catch(e){return null;}
}
function stage1BaselineSanityHtml(s){
 const n=stage1BaselineCount(s);
 const shown=n===null?'נמדד באזור החקירה':('<span class=\"baseline-number\">'+n+' rows</span>');
 return '<section class=\"card sanity-card stage1-baseline-check\" aria-label=\"Sanity Check\"><div class=\"sanity-title\">✓ SANITY CHECK · baseline נמדד</div><p><b>נקודת הבקרה:</b> ב-routes יש '+shown+'. זה המספר שאליו נשווה את תוצאת ה-JOIN. אין כאן עוד תחזית חדשה — רק מדידה של התחזית שכבר קבענו ב-Effect.</p></section>';
}
function stage1FinalSanityHtml(s){
 if(!lastResult)return'';
 const baseline=stage1BaselineCount(s);
 if(baseline===null)return '<div class=\"result-verify\"><b>Sanity Check:</b> השוו את מספר ה-rows ל-baseline שמדדתם על routes.</div>';
 const rows=lastResult.values.length;
 const ok=rows===baseline;
 return '<div class=\"result-verify '+(ok?'stage1-sanity-pass':'stage1-sanity-warn')+'\"><b>Sanity Check:</b> Baseline: <span class=\"inline-ltr\">'+baseline+' routes</span> · Query result: <span class=\"inline-ltr\">'+rows+' rows</span> · '+(ok?'✓ מספר ה-rows תואם לתחזית.':'⚠ מספר ה-rows השתנה. חזרו לתנאי החיבור ול-cardinality.')+'</div>';
}
function stage1JoinPredicateHtml(){
 return '<section class=\"card stage1-algebra-card\"><div class=\"algebra-title\">מהאלגברה הרלציונית ל-ON</div><p>אפשר לחשוב על INNER JOIN כמכפלה קרטזית ואז Selection לפי predicate שמחליט אילו זוגות נשארים:</p><pre>routes ⋈ depots\n= σ_{routes.depot_id = depots.depot_id}(routes × depots)</pre><p>אותו predicate נכתב ב-SQL כך:</p><pre>FROM routes r\nINNER JOIN depots d\n  ON r.depot_id = d.depot_id</pre><div class=\"algebra-principle\"><b>העיקרון:</b> <span class=\"inline-ltr\">ON r.depot_id = d.depot_id</span> הוא ה-predicate שקובע אילו tuples משתי ה-relations הם matches.</div></section>';
}

function stage1ExplorationHtml(s){
"""
replace_once(explore_anchor, explore_helpers, 'stage1 sanity helpers')

flow_old = "function stage1GuidedFlowHtml(s){\n if(state.stage!==1)return '';\n if(!stage1ReasoningResolved(s))return '';\n let out=stage1ExplorationHtml(s);\n if((state.exploreRan||{})[1])out+=sanityHtml(s,false);\n if((state.exploreRan||{})[1]&&stage1SanityResolved(s))out+=operationHtml(s)+joinVizDisclosureHtml(s);\n return out;\n}\n"
flow_new = "function stage1GuidedFlowHtml(s){\n if(state.stage!==1)return '';\n if(!stage1ReasoningResolved(s))return '';\n let out=stage1ExplorationHtml(s);\n if((state.exploreRan||{})[1])out+=stage1BaselineSanityHtml(s)+operationHtml(s);\n if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);\n return out;\n}\n"
replace_once(flow_old, flow_new, 'stage1 guided flow')

run_old = " try{exploreResult=exec(val);exploreError='';state.exploreRan[1]=true;}\n catch(e){exploreResult=null;exploreError=friendlySqlError(e.message,val,1);state.exploreRan[1]=false;}\n"
run_new = " try{\n   exploreResult=exec(val);exploreError='';state.exploreRan[1]=true;\n   const n=Number(exploreResult&&exploreResult.values&&exploreResult.values[0]&&exploreResult.values[0][0]);\n   if(Number.isFinite(n))state.stage1BaselineCount=n;\n }\n catch(e){exploreResult=null;exploreError=friendlySqlError(e.message,val,1);state.exploreRan[1]=false;}\n"
replace_once(run_old, run_new, 'store stage1 baseline')

# 5) Stage 1 correlated subquery is clearly an optional advanced challenge.
solution_tabs_old = "   out+='<div class=\"solutionbox\"><div class=\"solution-tabs\">'+options.map((x,i)=>'<button class=\"solution-option '+(choice===i?'active':'')+'\" data-solution-choice=\"'+i+'\">פתרון '+(i+1)+' · '+esc(x.label)+'</button>').join('')+'</div>';\n   if(state.stage===1&&choice===1)out+=stage1CorrelatedVizHtml();\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';\n"
solution_tabs_new = "   const tabs=options.map((x,i)=>{\n     const advanced=state.stage===1&&i===1;\n     const label=advanced?'אתגר מתקדם · בלי JOIN':('פתרון '+(i+1)+' · '+esc(x.label));\n     return '<button class=\"solution-option '+(advanced?'advanced ':'')+(choice===i?'active':'')+'\" data-solution-choice=\"'+i+'\">'+label+'</button>';\n   }).join('');\n   out+='<div class=\"solutionbox\"><div class=\"solution-tabs\">'+tabs+'</div>';\n   if(state.stage===1&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>אתגר מתקדם · לא צריך לשלוט בזה עדיין</b><p>זו דרך תקינה שמחזירה את אותה תוצאה בלי JOIN, אבל היא דורשת להבין query פנימית שתלויה ב-row של query חיצונית. פתחו אותה רק אם רוצים לראות דרך חשיבה נוספת.</p></div>'+stage1CorrelatedVizHtml();\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';\n"
replace_once(solution_tabs_old, solution_tabs_new, 'advanced solution tab')

# Stage 1 final result uses the measured baseline instead of repeating generic prose.
verify_old = "+(lastResult&&s.sanity?'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>':'')+\n"
verify_new = "+(lastResult&&s.sanity?(state.stage===1?stage1FinalSanityHtml(s):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')+\n"
replace_once(verify_old, verify_new, 'stage1 final sanity compare')

# Guardrails: Stage 2+ anchors remain present and no Stage 1 choice-based sanity is rendered in the guided flow.
required = [
    'מי שייך לכל אתר?',
    'function stage1JoinPredicateHtml()',
    'stage1BaselineSanityHtml(s)+operationHtml(s)',
    'אתגר מתקדם · בלי JOIN',
    'stage1OperationWrongFeedback(cur)',
    'stage1PredictionWrongFeedback(qi,cur)'
]
for token in required:
    if token not in s:
        raise SystemExit(f'missing guardrail token: {token}')
if 'if((state.exploreRan||{})[1])out+=sanityHtml(s,false);' in s:
    raise SystemExit('old Stage 1 sanity choice flow still present')

path.write_text(s, encoding='utf-8')
print('patched', path)
