from pathlib import Path
import re

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s=s.replace(old,new,1)

# Replace only the Stage 2 data object; Stage 1 and Stage 3+ stay untouched.
lines=s.splitlines()
idx=[i for i,line in enumerate(lines) if line.startswith('{title:"מי שייך לכל אתר?"')]
if len(idx)!=1:
    raise SystemExit(f'Stage 2 object: expected 1 line, found {len(idx)}')
lines[idx[0]]='{title:"מי שייך לכל אתר?",short:"נהגים לפי depot",eye:"חיבור מידע · להעביר את העיקרון",joinViz:"inner",context:"מנהלת המשמרת מכינה directory תפעולי ורוצה לראות את הנהגים תחת האתר שבו הם משובצים.",task:"ה-directory צריך לאפשר למנהלת המשמרת לזהות כל driver, את האתר שאליו הוא משויך ואת סוג הרישיון המדווח שלו.",output:"depot_name, driver_name, license_class · מיון לפי driver_id.",pred:"מיישמים את אותה דרך חשיבה מפרק 1: Grain → מידע חסר → קשר בין relations → Cardinality → מה יקרה ל-row → NULL.",predQuiz:[{q:"בבקשה העסקית הזאת, מה כל row בתוצאה צריכה לייצג?",opts:[["depot","depot"],["driver","driver"],["route","route"],["vehicle","vehicle"]],ans:"driver",why:"הבקשה היא directory של נהגים. לכן כל row בתוצאה צריכה לייצג driver אחת.",concept:"Output Grain = driver — כל row בתוצאה מייצגת driver אחת."},{q:"מתוך המידע שהבקשה דורשת, איזה פריט לא נמצא ב-drivers ולכן צריך להגיע מ-relation אחרת?",opts:[["depot_name","depot_name"],["driver_name","driver_name"],["license_class","license_class"],["hired_at","hired_at"]],ans:"depot_name",why:"driver_name ו-license_class כבר נמצאים ב-drivers. depot_name נמצא ב-depots, ולכן צריך את depots כדי להביא אותו."},{q:"לכל driver, כמה depots יכולים להתאים דרך depot_id?",opts:[["zero","0"],["one","1"],["many","many"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"one",why:"drivers.depot_id הוא Foreign Key וגם NOT NULL, ולכן הערך חייב להתאים ל-depot_id שקיים ב-depots. מכיוון ש-depots.depot_id הוא Primary Key, לכל driver מתאים depot אחד בדיוק. בכיוון ההפוך, depot אחד יכול להיות קשור ל-0, 1 או הרבה drivers.",concept:"Cardinality: depots 1:M drivers — depot הוא צד ה-1; drivers הן צד ה-M."},{q:"אם לכל driver מתאים depot אחד בדיוק, מה יקרה אחרי החיבור?",opts:[["same","כל driver תישאר שורה אחת"],["multiply","drivers יוכפלו"],["drop","חלק מה-drivers ייעלמו"],["aggregate","כמה drivers יאוחדו לשורה אחת"]],ans:"same",why:"אנחנו מתחילים מ-drivers, צד ה-M בקשר. לכל driver יש match יחיד ב-depots, צד ה-1, ולכן driver לא מתפצלת לכמה rows. ה-Grain נשאר driver ומספר ה-rows נשמר."},{q:"ל-driver שלא דווח עבורה license_class, מה יקרה ל-row בתוצאה?",opts:[["null","ה-driver תישאר וה-license_class יהיה NULL"],["drop","ה-row תיעלם"],["zero","יופיע 0"],["empty","תופיע מחרוזת ריקה"]],ans:"null",why:"license_class הוא attribute שמותר לו להיות NULL. NULL אומר שחסר value ב-attribute הזה; ה-driver עצמה עדיין קיימת ולכן ה-row נשארת.",concept:"NULL = חסר value ב-attribute, לא חסרה row."}],lesson:"אותה מסגרת מפרק 1 עובדת גם כאן: Grain של driver, קשר depots 1:M drivers, match אחד לכל driver, ולכן ה-JOIN שומר על ה-Grain. NULL ב-attribute אינו מוחק את ה-row.",operation:{"mode":"guided","tool":"INNER JOIN","model":"drivers.depot_id הוא NOT NULL Foreign Key אל depots.depot_id, שהוא Primary Key.","need":"עכשיו צריך לבחור פעולה שמוסיפה לכל driver את depot_name מה-depot שמתאים ל-depot_id שלה, בלי לשנות את Grain של driver.","q":"איזו פעולה מתאימה לצירוף ה-depot התואם אל כל driver?","opts":[["inner","INNER JOIN"],["exists","EXISTS"],["left","LEFT OUTER JOIN"],["group","GROUP BY"]],"ans":"inner","why":"אנחנו צריכים את depot_name בתוך ה-output row, ולכל driver יש depot תואם אחד בדיוק. INNER JOIN מחבר את ה-row התואמת מ-depots אל ה-driver.","hint":"צריך להביא value מ-depots אל ה-output, לא רק לבדוק אם depot קיים.","alt":"Correlated subquery יכולה להביא את depot_name, אבל JOIN מבטא ישירות את הקשר בין ה-relations."},sanity:{"baselineSql":"SELECT COUNT(*) AS driver_count FROM drivers;","q":"לפי ה-Grain וה-Cardinality שקבענו, איך מספר ה-rows אחרי ה-JOIN אמור להיות ביחס למספר ה-rows ב-drivers?","opts":[["same","אותו מספר rows"],["more","יותר rows"],["less","פחות rows"],["unknown","אי אפשר לצפות"]],"ans":"same","why":"ה-Grain הוא driver ולכל driver יש match אחד ב-depots, ולכן החיבור לא אמור להכפיל או להעלים drivers.","after":"השוו ל-baseline של drivers: התוצאה צריכה להכיל 11 rows. גם driver עם license_class = NULL צריכה להישאר בתוצאה."},altSolutions:[{"label":"Correlated subquery","sql":"SELECT (SELECT d.depot_name FROM depots d WHERE d.depot_id=dr.depot_id) AS depot_name,dr.driver_name,dr.license_class FROM drivers dr ORDER BY dr.driver_id;"}],starter:"",expected:"SELECT d.depot_name,dr.driver_name,dr.license_class FROM depots d INNER JOIN drivers dr ON dr.depot_id=d.depot_id ORDER BY dr.driver_id;",note:"העבירו את דרך החשיבה מפרק 1 ל-relation חדשה, ואז בדקו מה NULL משנה — ומה הוא לא משנה.",hints:["מה כל row צריכה לייצג?","איזה attribute חסר ב-drivers?","drivers.depot_id הוא Foreign Key אל depots.depot_id."],solution:"SELECT d.depot_name,dr.driver_name,dr.license_class FROM depots d INNER JOIN drivers dr ON dr.depot_id=d.depot_id ORDER BY dr.driver_id;",principle:"ביחס depots 1:M drivers, התחלה מצד ה-M וחיבור parent יחיד שומרים על Grain של driver; NULL ב-attribute נשאר בתוך אותה row."},'
s='\n'.join(lines)+'\n'

# Stage 2 has a new guided question sequence, so reset only Stage 2 learning-state once.
replace_once('const STAGE1_FLOW_VERSION=3;','const STAGE1_FLOW_VERSION=3;\nconst STAGE2_FLOW_VERSION=1;','stage2 flow constant')
replace_once('skeletonOpen:{},stage1FlowVersion:STAGE1_FLOW_VERSION});','skeletonOpen:{},stage1FlowVersion:STAGE1_FLOW_VERSION,stage2FlowVersion:STAGE2_FLOW_VERSION});','defaults stage2 flow version')

marker=''' if((raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION){
   delete out.predAnswers[1];
   delete out.predChecked[1];
   delete out.sanityAnswers[1];
   delete out.sanityChecked[1];
   delete out.operationAnswers[1];
   delete out.operationChecked[1];
   delete out.operationHints[1];
   delete out.operationOpen[1];
   delete out.exploreSql[1];
   delete out.exploreRan[1];
   delete out.graphOpen[1];
   delete out.hint[1];
   delete out.solution[1];
   out.completed=(out.completed||[]).filter(i=>i!==1);
   out.attempted=(out.attempted||[]).filter(i=>i!==1);
   out.stage1FlowVersion=STAGE1_FLOW_VERSION;
 }
'''
stage2_migration=marker+''' if((raw.stage2FlowVersion||0)<STAGE2_FLOW_VERSION){
   delete out.predAnswers[2];
   delete out.predChecked[2];
   delete out.sanityAnswers[2];
   delete out.sanityChecked[2];
   delete out.operationAnswers[2];
   delete out.operationChecked[2];
   delete out.operationHints[2];
   delete out.operationOpen[2];
   delete out.hint[2];
   delete out.solution[2];
   out.completed=(out.completed||[]).filter(i=>i!==2);
   out.attempted=(out.attempted||[]).filter(i=>i!==2);
   out.stage2FlowVersion=STAGE2_FLOW_VERSION;
 }
'''
replace_once(marker,stage2_migration,'stage2 state migration')
replace_once("if((raw.version||0)<APP_STATE_VERSION||(raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));","if((raw.version||0)<APP_STATE_VERSION||(raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION||(raw.stage2FlowVersion||0)<STAGE2_FLOW_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));",'save migrated stage2 state')

# Stage 2 reasoning completion helpers.
replace_once('''function stage1SanityResolved(s){
 return state.stage===1&&!!((state.exploreRan||{})[1]);
}
''','''function stage1SanityResolved(s){
 return state.stage===1&&!!((state.exploreRan||{})[1]);
}
function stage2ReasoningResolved(s){
 return state.stage===2&&Array.isArray(s.predQuiz)&&s.predQuiz.every((_,qi)=>predQuestionResolved(2,s,qi));
}
function stage2SanityResolved(s){
 return state.stage===2&&!!((state.sanityChecked||{})[2]&&(state.sanityAnswers||{})[2]===s.sanity.ans);
}
''','stage2 reasoning helpers')

# Stage 2 schema/cardinality bridge. Reuse the existing Stage 1 visual classes so no global UI redesign is needed.
stage2_helpers='''function stage2RelationsHtml(){
 return '<div class="stage1-relations">'+
 '<section class="stage1-relation"><h4>drivers</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>driver_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_id</td><td class="stage1-key">FK → depots.depot_id · NOT NULL</td></tr>'+
 '<tr><td>driver_name</td><td>NOT NULL</td></tr>'+
 '<tr><td>license_class</td><td>NULL allowed</td></tr>'+
 '<tr><td>hired_at</td><td>NOT NULL</td></tr>'+
 '<tr><td>supervisor_id</td><td>FK → drivers.driver_id · NULL allowed</td></tr>'+
 '</tbody></table></section>'+
 '<section class="stage1-relation"><h4>depots</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>depot_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_name</td><td>NOT NULL</td></tr>'+
 '<tr><td>region</td><td>NOT NULL</td></tr>'+
 '<tr><td>opened_at</td><td>NOT NULL</td></tr>'+
 '</tbody></table></section></div>';
}
function stage2KeyGuideHtml(){
 return '<div class="stage1-key-guide"><h4>איך drivers ו-depots קשורות?</h4><div class="key-link">drivers.depot_id (FK) → depots.depot_id (PK)</div><ul><li><b>FK + NOT NULL</b> ב-drivers: לכל driver חייב להיות depot_id שמתאים ל-depot קיים.</li><li><b>PK</b> ב-depots: אותו depot_id מזהה depot אחת בלבד.</li></ul><p class="key-arrow-note">כמו בפרק 1, החץ מציג את קשר ה-FK. את ה-Cardinality מסיקים מהמפתחות ומהאילוצים.</p></div>';
}
function stage2CardinalityMapHtml(){
 return '<div class="stage1-cardinality-map"><h4>ה-Cardinality כאן</h4><div class="cardinality-line">depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;drivers</div><p><b>depots הוא צד ה-1; drivers הן צד ה-M.</b></p><p>כל driver שייכת ל-depot אחד. depot אחד יכול להיות קשור ל-0, 1 או הרבה drivers.</p></div>';
}
function stage2PredictionWrongFeedback(qi,choice){
 const hints={
   0:{depot:'הבקשה היא directory של נהגים. מה אמור להופיע פעם אחת בכל row — depot או driver?',route:'route אינה יחידת הרשימה כאן; הבקשה עוסקת בנהגים.',vehicle:'vehicle יכול להיות קשור ל-driver או למסלול, אבל הוא לא היחידה שה-directory מבקש.'},
   1:{driver_name:'driver_name כבר נמצא ב-drivers. חפשו את הפריט שהבקשה דורשת ונמצא ב-depots.',license_class:'license_class כבר נמצא ב-drivers. איזה מידע על האתר חסר?',hired_at:'hired_at כבר נמצא ב-drivers. חפשו attribute שצריך להגיע מ-depots.'},
   2:{zero:'drivers.depot_id הוא NOT NULL Foreign Key, ולכן לכל driver חייב להיות depot קיים.',many:'depots.depot_id הוא Primary Key. אותו depot_id לא יכול לזהות כמה depots שונות.',unknown:'ה-schema כן מספיק: FK + NOT NULL בצד drivers ו-PK בצד depots קובעים match אחד לכל driver.'},
   3:{multiply:'כדי ש-driver תתפצל צריך שיהיו לה כמה matches ב-depots. חזרו ל-Cardinality.',drop:'לכל driver יש depot תואם אחד, ולכן אין כאן driver בלי match שאמורה להיעלם.',aggregate:'אין כאן aggregation; אנחנו מוסיפים depot_name ל-row של driver.'},
   4:{drop:'NULL הוא חוסר value ב-attribute, לא היעדר של ה-driver row.',zero:'NULL אינו 0. אלה ערכים שונים.',empty:'NULL אינו מחרוזת ריקה; הוא מציין שאין value מדווח.'}
 };
 return (hints[qi]&&hints[qi][choice])||'חזרו ל-Grain, לסכמה ול-Cardinality שקבעתם.';
}

'''
replace_once('function stage1PredictionWrongFeedback(qi,choice){',stage2_helpers+'function stage1PredictionWrongFeedback(qi,choice){','stage2 display helpers')

# Give Stage 2 the same one-question-at-a-time reasoning flow as Stage 1, without reteaching definitions at length.
needle="""   return '<div class=\"pred-quiz\">'+out+'</div>';
 }
 const qs=s.predQuiz.map((q,qi)=>{"""
insert="""   return '<div class=\"pred-quiz\">'+out+'</div>';
 }
 if(state.stage===2){
   const renderQ=(qi,afterLabel='')=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(2,qi);
     const concept=(checked&&cur===q.ans&&q.concept)?'<div class=\"stage1-concept-close\"><b>המושג:</b> '+esc(q.concept)+'</div>':'';
     const answerText=cur===q.ans?q.why:stage2PredictionWrongFeedback(qi,cur);
     const exp=(checked&&cur)?('<div class=\"answer-exp '+(cur===q.ans?'good':'wrong')+'\"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(answerText)+concept+'</div>'):'';
     return '<div class=\"pred-q\"><label>'+(qi+1)+'. '+esc(q.q)+'</label>'+afterLabel+'<select data-predq=\"'+qi+'\"><option value=\"\">בחרו...</option>'+q.opts.map(o=>'<option value=\"'+esc(o[0])+'\" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class=\"actions\"><button class=\"check\" data-check-pred=\"'+qi+'\">✓ בדוק תשובה</button></div>'+exp+'</div>';
   };
   let out=renderQ(0);
   if(predQuestionResolved(2,s,0))out+=renderQ(1,stage2RelationsHtml());
   if(predQuestionResolved(2,s,1))out+=stage2KeyGuideHtml()+renderQ(2);
   if(predQuestionResolved(2,s,2))out+=stage2CardinalityMapHtml()+renderQ(3);
   if(predQuestionResolved(2,s,3))out+=renderQ(4);
   return '<div class=\"pred-quiz\">'+out+'</div>';
 }
 const qs=s.predQuiz.map((q,qi)=>{"""
replace_once(needle,insert,'stage2 sequential prediction flow')

# Stage 2 suppresses the old duplicate model/lesson block and uses the same business-decomposition title.
replace_once("const attemptedPred=s.predQuiz?(state.stage===1?stage1ReasoningResolved(s):s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi))):(s.requireNote?noteStarted:true);","const attemptedPred=s.predQuiz?(state.stage===1?stage1ReasoningResolved(s):(state.stage===2?stage2ReasoningResolved(s):s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi)))):(s.requireNote?noteStarted:true);",'stage2 attempted prediction')
replace_once("const followup=state.stage===1?'':((model||lesson)?'<div id=\"predictionFollowup\" class=\"prediction-followup '+(attemptedPred?'':'is-hidden')+'\">'+model+lesson+'</div>':'');","const followup=(state.stage===1||state.stage===2)?'':((model||lesson)?'<div id=\"predictionFollowup\" class=\"prediction-followup '+(attemptedPred?'':'is-hidden')+'\">'+model+lesson+'</div>':'');",'stage2 no duplicate followup')
replace_once("const stageTitle=state.stage===1?'מפרקים את הבקשה העסקית':'המודל הרלציוני';","const stageTitle=(state.stage===1||state.stage===2)?'מפרקים את הבקשה העסקית':'המודל הרלציוני';",'stage2 relational title')

# Operation is a normal visible step in Stage 2, not a collapsed help box.
replace_once("if(state.stage===1)return '<section class=\"card operation-card\"><div class=\"operation-title\">בחירת הפעולה</div>'+body+'</section>';","if(state.stage===1||state.stage===2)return '<section class=\"card operation-card\"><div class=\"operation-title\">בחירת הפעולה</div>'+body+'</section>';",'stage2 visible operation card')

# Gate Stage 2: reasoning -> operator -> sanity -> SQL.
replace_once('''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=stage1BaselineSanityHtml(s)+operationHtml(s);
 if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}
''','''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=stage1BaselineSanityHtml(s)+operationHtml(s);
 if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}
function stage2GuidedFlowHtml(s){
 if(state.stage!==2||!stage2ReasoningResolved(s))return '';
 let out=operationHtml(s);
 if(operationChoiceResolved(s))out+=sanityHtml(s,false)+joinVizDisclosureHtml(s);
 return out;
}
''','stage2 guided flow')

replace_once("(state.stage===1?stage1GuidedFlowHtml(s):(operationHtml(s)+joinVizDisclosureHtml(s)+sanityHtml(s,false)))+","(state.stage===1?stage1GuidedFlowHtml(s):(state.stage===2?stage2GuidedFlowHtml(s):(operationHtml(s)+joinVizDisclosureHtml(s)+sanityHtml(s,false))))+",'render stage2 guided flow')
replace_once("((s.summary||s.intro||!scaffoldComplete(s)||(state.stage===1&&!operationChoiceResolved(s)))?'':'<section class=\"editor\">","((s.summary||s.intro||!scaffoldComplete(s)||(state.stage===1&&!operationChoiceResolved(s))||(state.stage===2&&!stage2SanityResolved(s)))?'':'<section class=\"editor\">",'gate stage2 SQL editor')

# Guardrails: keep scope narrow and ensure all agreed Stage 2 concepts exist.
required=[
    'const STAGE2_FLOW_VERSION=1;',
    'Output Grain = driver',
    'renderQ(1,stage2RelationsHtml())',
    'drivers.depot_id (FK) → depots.depot_id (PK)',
    'depots&nbsp;&nbsp; 1 ───── M &nbsp;&nbsp;drivers',
    'depots הוא צד ה-1; drivers הן צד ה-M.',
    'NULL = חסר value ב-attribute, לא חסרה row.',
    'function stage2GuidedFlowHtml(s)',
    'state.stage===2&&!stage2SanityResolved(s)'
]
for text in required:
    if text not in s:
        raise SystemExit(f'missing required Stage 2 text: {text}')

p.write_text(s,encoding='utf-8')
print('patched',p)
