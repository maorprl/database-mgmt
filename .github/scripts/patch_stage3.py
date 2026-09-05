from pathlib import Path
import re

p = Path('sql-lab/index.html')
s = p.read_text(encoding='utf-8')
old = s


def repl(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        raise SystemExit(f'expected {n} occurrences, found {c}: {a[:120]!r}')
    s = s.replace(a, b, n)


# Stage 3 content: Grain -> child role -> two 1:M branches -> fan-out -> raw JOIN Grain -> Sanity -> EXISTS -> SQL.
pat = r'^\{title:"אילו אתרים באמת פעילים\?".*$'
ms = re.findall(pat, s, flags=re.M)
if len(ms) != 1:
    raise SystemExit(f'expected one Stage 3 line, found {len(ms)}')
new_stage = r'''{title:"אילו אתרים באמת פעילים?",short:"נהג וגם מסלול",eye:"שני ענפי 1:M · קיום בלי fan-out",trapId:"early-fanout",fanoutTrap:true,scratch:"ציירו depot במרכז, drivers בענף אחד ו-routes בענף שני. השאירו ליד כל קו מקום לכתוב את ה-Cardinality אחרי שתסיקו אותה.",context:"מנהלת הרשת רוצה רשימת depots שיש בהם לפחות driver אחד ולפחות route אחת. היא אינה צריכה פרטי נהגים או מסלולים.",task:"בנו shortlist שבו כל depot מתאים מופיע פעם אחת בלבד: רק depots שיש בהם גם driver אחד לפחות וגם route אחת לפחות.",output:"depot_name · מיון לפי depot_id.",pred:"מפרקים את הבקשה: Grain → מה באמת צריך מה-child relations → Cardinality בשני הענפים → מה JOIN גולמי יעשה ל-Grain → Sanity → בחירת פעולה.",predQuiz:[{q:"בבקשה העסקית הזאת, מה כל row בתוצאה צריכה לייצג?",opts:[["depot","depot"],["driver","driver"],["route","route"],["pair","driver × route"]],ans:"depot",why:"הבקשה היא shortlist של depots. לכן כל row בתוצאה צריכה לייצג depot אחת, גם אם כדי להחליט אם היא נכנסת לרשימה נבדוק relations אחרות.",concept:"Output Grain = depot — כל row בתוצאה מייצגת depot אחת."},{q:"מה אנחנו באמת צריכים מ-drivers ומ-routes כדי לענות לבקשה?",opts:[["existence","רק לדעת אם קיימת לפחות row אחת בכל relation"],["driver-details","להוסיף פרטי driver לפלט"],["route-details","להוסיף פרטי route לפלט"],["all-details","להוסיף גם driver וגם route לפלט"]],ans:"existence",why:"הפלט מבקש רק depot_name. drivers ו-routes משמשות כאן כתנאי: האם קיימת לפחות driver אחת והאם קיימת לפחות route אחת. אין צורך להכניס child rows או attributes שלהן לפלט."},{q:"מה ה-Cardinality בשני הענפים שיוצאים מ-depots?",opts:[["both-1m","depots 1:M drivers וגם depots 1:M routes"],["both-11","depots 1:1 drivers וגם depots 1:1 routes"],["reverse","drivers 1:M depots וגם routes 1:M depots"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"both-1m",why:"drivers.depot_id ו-routes.depot_id הם Foreign Keys שאינם UNIQUE. לכן depot אחת יכולה להיות קשורה לכמה drivers ובנפרד לכמה routes.",concept:"Cardinality: depots 1:M drivers וגם depots 1:M routes — שני ענפי M נפרדים מאותו parent."},{q:"ב-Riverbend Crossdock יש 3 drivers ו-3 routes. אם נחבר את שני ענפי ה-M לאותה depot ב-JOIN גולמי, כמה rows ייווצרו עבורה?",opts:[["3","3"],["6","6"],["9","9"],["1","1"]],ans:"9",why:"כל אחת מ-3 ה-drivers יכולה להופיע עם כל אחת מ-3 ה-routes של אותה depot. לכן מתקבלים 3×3 = 9 combinations.",concept:"Fan-out: חיבור שני ענפי 1:M יכול להכפיל child rows זה בזה."},{q:"אחרי JOIN גולמי כזה, מה row אחת בתוצאת הביניים מייצגת?",opts:[["depot","depot אחת"],["driver","driver אחת"],["route","route אחת"],["pair","שילוב של driver אחת ו-route אחת בתוך depot"]],ans:"pair",why:"כל row של החיבור הגולמי מכילה child row אחת מ-drivers ו-child row אחת מ-routes ששייכות לאותה depot. לכן ה-Grain של תוצאת הביניים כבר אינו depot אלא combination של driver × route בתוך depot.",concept:"Raw JOIN Grain = driver × route בתוך depot — לא ה-Grain העסקי שביקשנו."}],lesson:"בפרק הזה ה-JOIN עצמו יכול לשנות את רמת הפירוט: שני ענפי 1:M יוצרים combinations. כשצריך רק לדעת אם child row קיימת, עדיף לבדוק קיום בלי לצרף את child rows לפלט.",operation:{"mode":"guided","tool":"EXISTS","model":"depots הוא ה-parent; drivers ו-routes הם שני ענפי 1:M נפרדים. הבקשה צריכה רק קיום בכל ענף.","need":"כבר קבענו שה-Grain העסקי הוא depot, ושאנחנו צריכים רק לבדוק אם יש לפחות driver אחת ולפחות route אחת — בלי ליצור driver×route combinations.","q":"איזו פעולה מבטאת בדיקת קיום בלי לצרף את child rows לתוצאה?","opts":[["exists","EXISTS"],["inner","INNER JOIN לשני הענפים"],["distinct","JOIN + DISTINCT"],["group","JOIN + GROUP BY"]],"ans":"exists","why":"EXISTS עונה ישירות על השאלה 'האם קיימת לפחות row אחת שמתאימה?'. הוא מסנן את ה-depot row בלי להוסיף child rows, ולכן אינו יוצר fan-out ושומר על Grain של depot.","hint":"חפשו פעולה שמחזירה תשובת קיום עבור ה-depot הנוכחית, ולא פעולה שמצרפת את child rows עצמם.","alt":"JOIN + DISTINCT יכול לתת את אותה רשימת שמות בדאטה הנוכחי, אבל הוא יוצר קודם את ה-fan-out ורק אחר כך מסיר חזרות."},sanity:{"q":"Riverbend יצרה 9 rows בחיבור הגולמי, אבל ה-Output Grain המבוקש הוא depot. כמה פעמים Riverbend צריכה להופיע בתוצאה הסופית?","opts":[["one","פעם אחת"],["three","3 פעמים"],["six","6 פעמים"],["nine","9 פעמים"]],"ans":"one","why":"ה-Sanity Check חוזר לבקשה העסקית: row אחת = depot. מספר ה-drivers וה-routes קובע אם depot נכנסת לרשימה, לא כמה פעמים היא מופיעה.","after":"Riverbend Crossdock צריכה להופיע פעם אחת בלבד. בכלל התוצאה אמורות להיות 7 depots; אם קיבלתם יותר rows, בדקו אם יצרתם fan-out."},altSolutions:[{"label":"JOIN + DISTINCT","sql":"SELECT DISTINCT d.depot_name FROM depots d INNER JOIN drivers dr ON dr.depot_id=d.depot_id INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY d.depot_id;"}],starter:"",expected:"SELECT d.depot_name FROM depots d WHERE EXISTS (SELECT 1 FROM drivers dr WHERE dr.depot_id=d.depot_id) AND EXISTS (SELECT 1 FROM routes r WHERE r.depot_id=d.depot_id) ORDER BY d.depot_id;",note:"אל תבחרו כלי לפני שקבעתם מה ה-child relations צריכות לתרום: rows לפלט, או רק תשובת קיום.",hints:["הפלט הוא depot_name בלבד — האם צריך child attributes?","שני ענפי 1:M יכולים ליצור driver×route combinations.","חפשו פעולה שבודקת אם match קיים בלי להוסיף אותו לפלט."],solution:"SELECT d.depot_name FROM depots d WHERE EXISTS (SELECT 1 FROM drivers dr WHERE dr.depot_id=d.depot_id) AND EXISTS (SELECT 1 FROM routes r WHERE r.depot_id=d.depot_id) ORDER BY d.depot_id;",principle:"כשצריך רק קיום משני ענפי 1:M, EXISTS שומר על Grain של ה-parent ומונע fan-out במקום לנקות אותו אחר כך."},'''
s = re.sub(pat, new_stage, s, count=1, flags=re.M)

# Stage 3 state version so old checked answers do not skip the new path.
repl('const STAGE2_FLOW_VERSION=1;', 'const STAGE2_FLOW_VERSION=1;\nconst STAGE3_FLOW_VERSION=1;')
repl('stage1FlowVersion:STAGE1_FLOW_VERSION,stage2FlowVersion:STAGE2_FLOW_VERSION});', 'stage1FlowVersion:STAGE1_FLOW_VERSION,stage2FlowVersion:STAGE2_FLOW_VERSION,stage3FlowVersion:STAGE3_FLOW_VERSION});')
marker = " out.theme=out.theme==='dark'?'dark':'light';"
if s.count(marker) != 1:
    raise SystemExit('migration marker not unique')
stage3_migration = ''' if((raw.stage3FlowVersion||0)<STAGE3_FLOW_VERSION){
   delete out.predAnswers[3];
   delete out.predChecked[3];
   delete out.sanityAnswers[3];
   delete out.sanityChecked[3];
   delete out.operationAnswers[3];
   delete out.operationChecked[3];
   delete out.operationHints[3];
   delete out.operationOpen[3];
   delete out.hint[3];
   delete out.solution[3];
   delete out.solutionChoice[3];
   out.completed=(out.completed||[]).filter(i=>i!==3);
   out.attempted=(out.attempted||[]).filter(i=>i!==3);
   out.stage3FlowVersion=STAGE3_FLOW_VERSION;
 }
'''
s = s.replace(marker, stage3_migration + marker, 1)
repl("if((raw.version||0)<APP_STATE_VERSION||(raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION||(raw.stage2FlowVersion||0)<STAGE2_FLOW_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));", "if((raw.version||0)<APP_STATE_VERSION||(raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION||(raw.stage2FlowVersion||0)<STAGE2_FLOW_VERSION||(raw.stage3FlowVersion||0)<STAGE3_FLOW_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));")

# Three-column relevant schema on desktop.
repl('.stage1-relations{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}', '.stage1-relations{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}.stage3-relations{grid-template-columns:repeat(3,minmax(0,1fr))}@media(max-width:900px){.stage3-relations{grid-template-columns:1fr}}')

helper_marker = 'function stage1PredictionWrongFeedback(qi,choice){'
if s.count(helper_marker) != 1:
    raise SystemExit('stage1 feedback marker not unique')
helpers = r'''function stage3ReasoningResolved(s){
 return state.stage===3&&Array.isArray(s.predQuiz)&&s.predQuiz.every((_,qi)=>predQuestionResolved(3,s,qi));
}
function stage3SanityResolved(s){
 return state.stage===3&&!!((state.sanityChecked||{})[3]&&(state.sanityAnswers||{})[3]===s.sanity.ans);
}
function stage3RelationsHtml(){
 return '<div class="stage1-relations stage3-relations">'+
 '<section class="stage1-relation"><h4>depots</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>depot_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_name</td><td>NOT NULL</td></tr>'+
 '</tbody></table></section>'+
 '<section class="stage1-relation"><h4>drivers</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>driver_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_id</td><td class="stage1-key">FK → depots.depot_id · NOT NULL</td></tr>'+
 '<tr><td>driver_name</td><td>NOT NULL</td></tr>'+
 '</tbody></table></section>'+
 '<section class="stage1-relation"><h4>routes</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>route_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_id</td><td class="stage1-key">FK → depots.depot_id · NOT NULL</td></tr>'+
 '<tr><td>route_code</td><td>UNIQUE · NOT NULL</td></tr>'+
 '</tbody></table></section></div>';
}
function stage3KeyGuideHtml(){
 return '<div class="stage1-key-guide"><h4>איך שלוש ה-relations קשורות?</h4><div class="key-link">drivers.depot_id (FK) → depots.depot_id (PK)<br>routes.depot_id (FK) → depots.depot_id (PK)</div><ul><li>גם driver וגם route שייכות ל-depot דרך <b>depot_id</b>.</li><li>בשני ה-child relations, <b>depot_id אינו UNIQUE</b> — לכן אותו depot_id יכול לחזור בכמה rows.</li><li>אין כאן FK ישיר בין driver ל-route; הן שני ענפים נפרדים של אותו parent.</li></ul><p class="key-arrow-note">החצים מציגים קשרי FK. עכשיו מסיקים מהם את ה-Cardinality בכל ענף.</p></div>';
}
function stage3CardinalityMapHtml(){
 return '<div class="stage1-cardinality-map"><h4>שני ענפי 1:M מאותו parent</h4><div class="cardinality-line">drivers&nbsp;&nbsp; M ───── 1 &nbsp;&nbsp;depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;routes</div><p><b>אלה שני קשרים נפרדים:</b> depot אחת יכולה להיות קשורה לכמה drivers, ובנפרד לכמה routes.</p><p>זה ש-driver ו-route שייכות לאותה depot לא יוצר ביניהן קשר אחד-לאחד.</p></div>';
}
function stage3GrainMismatchHtml(){
 return '<div class="stage1-concept-note"><h4>זה החידוש של פרק 3</h4><p><b>ה-Grain העסקי:</b> depot אחת לכל row.</p><p><b>ה-Grain של JOIN גולמי לשני הענפים:</b> combination של driver × route בתוך depot.</p><p>כלומר כאן JOIN לא רק מוסיף attributes — הוא יכול ליצור רמת פירוט חדשה ומיותרת. זה בדיוק ה-fan-out שאנחנו רוצים לזהות לפני כתיבת SQL.</p></div>';
}
function stage3PredictionWrongFeedback(qi,choice){
 const hints={
   0:{driver:'הבקשה אינה directory של drivers; היא shortlist של depots.',route:'הבקשה אינה רשימת routes; היא shortlist של depots.',pair:'driver × route הוא מה שעלול להיווצר בטעות בחיבור, לא מה שהעסק ביקש.'},
   1:{'driver-details':'אין driver attribute בדרישות הפלט. מה כן צריך לדעת על drivers?','route-details':'אין route attribute בדרישות הפלט. מה כן צריך לדעת על routes?','all-details':'הבקשה מדגישה שלא צריכים פרטי child rows — רק אם הן קיימות.'},
   2:{'both-11':'depot_id אינו UNIQUE ב-drivers או ב-routes, ולכן depot יכולה להופיע בכמה child rows.','reverse':'כל driver וכל route שייכות ל-depot אחת; הכיוון של ה-many הוא מה-depot אל child rows.','unknown':'ה-FK והעובדה ש-depot_id אינו UNIQUE ב-child relations נותנים מספיק מידע כדי להסיק 1:M בשני הענפים.'},
   3:{'3':'3 drivers לבדם נותנים 3 rows, אבל כל אחת מתחברת לכל אחת מ-3 routes.','6':'כאן לא מחברים 3+3 אלא את כל הצירופים האפשריים בין שני הענפים.','1':'row אחת היא ה-Grain העסקי הרצוי, אבל JOIN גולמי של 3 מול 3 יוצר יותר.'},
   4:{depot:'זה ה-Grain העסקי שאנחנו רוצים, אבל הסתכלו על row גולמית אחרי שחיברנו גם driver וגם route.',driver:'row כוללת גם route מסוימת, לכן driver לבדה אינה מתארת את רמת הפירוט.',route:'row כוללת גם driver מסוימת, לכן route לבדה אינה מתארת את רמת הפירוט.'}
 };
 return (hints[qi]&&hints[qi][choice])||'חזרו ל-Grain העסקי, לשני ענפי ה-1:M, ולמה שכל row בחיבור הגולמי מייצגת.';
}
function stage3OperationWrongFeedback(choice){
 if(choice==='inner')return 'INNER JOIN לשני הענפים מצרף את child rows עצמם, ולכן Riverbend יכולה להפוך ל-3×3 combinations. הבקשה צריכה רק תשובת קיום.';
 if(choice==='distinct')return 'JOIN + DISTINCT יכול לנקות חזרות בסוף, אבל ה-fan-out כבר נוצר. חפשו פעולה שבודקת קיום בלי ליצור את combinations מלכתחילה.';
 if(choice==='group')return 'GROUP BY יכול לקבץ שוב אחרי JOIN, אבל גם כאן קודם נוצרים child combinations. אין לנו מדד שדורש את child rows; צריך רק לדעת אם הן קיימות.';
 return 'חפשו פעולה שבודקת אם match קיים עבור ה-depot הנוכחית בלי לצרף את child rows לפלט.';
}
function stage3ExistsBridgeHtml(){
 return '<section class="card stage1-algebra-card"><div class="algebra-title">מהרעיון הרלציוני ל-EXISTS</div><p>ברמה הלוגית אנחנו מסננים את relation <b>depots</b>. עבור כל depot שואלים שתי שאלות קיום:</p><pre>∃ driver : driver.depot_id = depot.depot_id\nAND\n∃ route  : route.depot_id  = depot.depot_id</pre><p><b>∃</b> פירושו "קיים". מספיק match אחד; לא צריך לצרף את ה-child rows לתוצאה.</p><p>ב-SQL הרעיון הזה נכתב באמצעות <b>EXISTS</b>:</p><pre>FROM depots d\nWHERE EXISTS ( ... driver עם אותו depot_id ... )\n  AND EXISTS ( ... route עם אותו depot_id ... )</pre><div class="algebra-principle"><b>העיקרון:</b> ה-query החיצוני נשאר ברמת depot. כל EXISTS רק מחליט אם ה-depot row עוברת את הסינון — הוא לא מוסיף driver או route rows, ולכן ה-Grain נשאר depot.</div></section>';
}
function stage3GuidedFlowHtml(s){
 if(state.stage!==3||!stage3ReasoningResolved(s))return '';
 let out=sanityHtml(s,false);
 if(stage3SanityResolved(s))out+=operationHtml(s);
 if(stage3SanityResolved(s)&&operationChoiceResolved(s))out+=stage3ExistsBridgeHtml();
 return out;
}
function stage3SolutionExplanationHtml(choice){
 if(choice===0){
   return '<div class="stage1-concept-note"><h4>איך פתרון 1 עובד?</h4><p><b>1.</b> ה-query החיצוני מתחיל מ-depots, ולכן יחידת העבודה נשארת depot.</p><p><b>2.</b> EXISTS הראשון בודק אם קיימת driver עם אותו depot_id.</p><p><b>3.</b> EXISTS השני בודק אם קיימת route עם אותו depot_id.</p><p><b>4.</b> AND דורש ששתי בדיקות הקיום יהיו true. אף child row לא נכנסת לפלט, ולכן אין fan-out.</p></div>';
 }
 return '<div class="stage1-concept-note"><h4>איך פתרון 2 עובד?</h4><p><b>1.</b> שני ה-JOINs מצרפים בפועל את drivers ואת routes לכל depot.</p><p><b>2.</b> ב-depot עם 3 drivers ו-3 routes נוצרים קודם 9 driver×route combinations.</p><p><b>3.</b> DISTINCT מסיר אחר כך את שמות ה-depot החוזרים, כך שבדאטה הזה מתקבלת אותה רשימה סופית.</p><p><b>ההבדל המהותי:</b> EXISTS מונע את ה-fan-out; JOIN + DISTINCT יוצר אותו ואז מנקה את הפלט.</p></div>';
}

'''
s = s.replace(helper_marker, helpers + helper_marker, 1)

# Progressive Stage 3 question reveal.
quiz_marker = ' const qs=s.predQuiz.map((q,qi)=>{'
if s.count(quiz_marker) != 1:
    raise SystemExit('generic quiz marker not unique')
stage3_quiz = r''' if(state.stage===3){
   const renderQ=(qi,afterLabel='')=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(3,qi);
     const concept=(checked&&cur===q.ans&&q.concept)?'<div class="stage1-concept-close"><b>המושג:</b> '+esc(q.concept)+'</div>':'';
     const answerText=cur===q.ans?q.why:stage3PredictionWrongFeedback(qi,cur);
     const exp=(checked&&cur)?('<div class="answer-exp '+(cur===q.ans?'good':'wrong')+'"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(answerText)+concept+'</div>'):'';
     return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label>'+afterLabel+'<select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';
   };
   let out=renderQ(0);
   if(predQuestionResolved(3,s,0))out+=renderQ(1);
   if(predQuestionResolved(3,s,1))out+=stage3RelationsHtml()+stage3KeyGuideHtml()+renderQ(2);
   if(predQuestionResolved(3,s,2))out+=stage3CardinalityMapHtml()+renderQ(3);
   if(predQuestionResolved(3,s,3))out+=renderQ(4);
   if(predQuestionResolved(3,s,4))out+=stage3GrainMismatchHtml();
   return '<div class="pred-quiz">'+out+'</div>';
 }
'''
s = s.replace(quiz_marker, stage3_quiz + quiz_marker, 1)

# Stage 3 uses the same business-led wrapper as Stages 1-2.
repl("const attemptedPred=s.predQuiz?(state.stage===1?stage1ReasoningResolved(s):(state.stage===2?stage2ReasoningResolved(s):s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi)))):(s.requireNote?noteStarted:true);", "const attemptedPred=s.predQuiz?(state.stage===1?stage1ReasoningResolved(s):(state.stage===2?stage2ReasoningResolved(s):(state.stage===3?stage3ReasoningResolved(s):s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi))))):(s.requireNote?noteStarted:true);")
repl("const followup=(state.stage===1||state.stage===2)?'':((model||lesson)?", "const followup=(state.stage===1||state.stage===2||state.stage===3)?'':((model||lesson)?")
repl("const stageTitle=(state.stage===1||state.stage===2)?'מפרקים את הבקשה העסקית':'המודל הרלציוני';", "const stageTitle=(state.stage===1||state.stage===2||state.stage===3)?'מפרקים את הבקשה העסקית':'המודל הרלציוני';")

# Operation feedback and direct card for Stage 3.
repl("else if(checked)body+='<div class=\"op-feedback bad\"><b>עוד לא.</b> '+esc(state.stage===1?stage1OperationWrongFeedback(cur):'חזרו ל-Grain ולתפקיד של כל relation.')+'</div>';", "else if(checked)body+='<div class=\"op-feedback bad\"><b>עוד לא.</b> '+esc(state.stage===1?stage1OperationWrongFeedback(cur):(state.stage===3?stage3OperationWrongFeedback(cur):'חזרו ל-Grain ולתפקיד של כל relation.'))+'</div>';")
repl("if(state.stage===1||state.stage===2)return '<section class=\"card operation-card\">", "if(state.stage===1||state.stage===2||state.stage===3)return '<section class=\"card operation-card\">")

# Gate Stage 3 solutions until the operator was inferred, and explain both solutions.
repl("const allowFullSolution=state.stage!==1||operationChoiceResolved(s);", "const allowFullSolution=(state.stage===1||state.stage===3)?operationChoiceResolved(s):true;")
repl("else if(state.stage===2&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>פתרון 2 · Correlated subquery</b><p>כאן לא מסתפקים ב-SQL עצמו: מפרקים את אותה דרך lookup שלמדנו בפרק 1, הפעם על drivers, ובודקים גם איפה NULL נכנס לתמונה.</p></div>'+stage2CorrelatedVizHtml();\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';", "else if(state.stage===2&&choice===1)out+='<div class=\"advanced-solution-intro\"><b>פתרון 2 · Correlated subquery</b><p>כאן לא מסתפקים ב-SQL עצמו: מפרקים את אותה דרך lookup שלמדנו בפרק 1, הפעם על drivers, ובודקים גם איפה NULL נכנס לתמונה.</p></div>'+stage2CorrelatedVizHtml();\n   else if(state.stage===3)out+=stage3SolutionExplanationHtml(choice)+'<pre>'+esc(options[choice].sql)+'</pre>';\n   else out+='<pre>'+esc(options[choice].sql)+'</pre>';")

# Guided flow router and editor gate.
repl("(state.stage===1?stage1GuidedFlowHtml(s):(state.stage===2?stage2GuidedFlowHtml(s):(operationHtml(s)+joinVizDisclosureHtml(s)+sanityHtml(s,false))))", "(state.stage===1?stage1GuidedFlowHtml(s):(state.stage===2?stage2GuidedFlowHtml(s):(state.stage===3?stage3GuidedFlowHtml(s):(operationHtml(s)+joinVizDisclosureHtml(s)+sanityHtml(s,false)))))")
repl("((s.summary||s.intro||!scaffoldComplete(s)||(state.stage===1&&!operationChoiceResolved(s))||(state.stage===2&&!stage2SanityResolved(s)))?'':'<section class=\"editor\">", "((s.summary||s.intro||!scaffoldComplete(s)||(state.stage===1&&!operationChoiceResolved(s))||(state.stage===2&&!stage2SanityResolved(s))||(state.stage===3&&(!stage3SanityResolved(s)||!operationChoiceResolved(s))))?'':'<section class=\"editor\">")

if s == old:
    raise SystemExit('no changes made')
p.write_text(s, encoding='utf-8')
