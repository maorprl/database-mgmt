from pathlib import Path
import re

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')


def replace_once(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1 match, got {c}')
    s=s.replace(old,new,1)

# Keep Stage 2 source object byte-for-byte identical as a guardrail.
stage2_marker='{title:"מי שייך לכל אתר?"'
stage3_marker='{title:"אילו אתרים באמת פעילים?"'
start2=s.index(stage2_marker)
end2=s.index(stage3_marker,start2)
stage2_before=s[start2:end2]

old_stage1='''{title:"איפה יצא כל מסלול?",short:"מסלולים לפי depot",eye:"חיבור מידע · חזרות תקינות",joinViz:"inner",context:"חדר הבקרה רוצה יומן מסלולים שמוסיף לכל route את האתר שממנו יצא.",task:"בנו רשימה של כל מסלול עם שם ה-depot, תאריך השירות, הסטטוס והמרחק.",output:"depot_name, route_code, service_date, status, distance_km · מיון לפי route_id.",pred:"קבעו מה כל row בתוצאה מייצגת לפני שאתם כותבים SQL.",predQuiz:[{q:"מה ה-output Grain?",opts:[["depot","depot"],["route","route"],["vehicle","vehicle"],["stop","stop"]],ans:"route",why:"כל row מייצגת route אחת, עם פרטי ה-depot שממנו יצאה."}],lesson:"הקשר הוא `depots 1:M routes`: depot אחד יכול להיות קשור לכמה routes, וכל route שייכת ל־depot אחד.",operation:{"mode":"teach","tool":"INNER JOIN","newTool":"INNER JOIN","model":"ב־routes נמצא depot_id, וב־depots נמצא depot_id שמזהה כל depot. בדקו בסכמה איזה מהם Foreign Key ואיזה Primary Key.","need":"להוסיף לכל route את שם ה-depot שלו, בלי לשנות את מספר המסלולים.","why":"בכל route יש depot_id שמצביע על depot קיים. אנחנו רוצים להוסיף את שם ה-depot לאותה row של route. INNER JOIN מחזיר את ה-route יחד עם ה-depot שאליו היא מצביעה.","alt":"אפשר לקבל את אותה תוצאה גם עם subquery שמחפשת את שם ה-depot לכל route. זו דרך תקינה, אבל JOIN מציג את הקשר ביניהן ישירות."},sanity:{"baselineSql":"SELECT COUNT(*) AS route_count FROM routes;","q":"Baseline: ב־`routes` יש 13 rows. הקשר הוא `depots 1:M routes`. אם לכל route יש depot תואם, כמה rows אתם מצפים לקבל בתוצאה?","opts":[["8","8 שורות"],["13","13 שורות"],["21","21 שורות"],["104","104 שורות"]],"ans":"13","why":"ה־Grain נשאר route. צירוף פרטי ה־depot לא יוצר route חדשה ולא מפצל route קיימת, ולכן 13 routes נשארות 13 rows.","after":"בדקו שבתוצאה יש 13 rows — כמו מספר ה־rows המקורי ב־`routes`."},altSolutions:[{"label":"Correlated subquery","sql":"SELECT (SELECT d.depot_name FROM depots d WHERE d.depot_id=r.depot_id) AS depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM routes r ORDER BY r.route_id;"}],starter:"",expected:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",note:"קבעו את ה-Grain לפני החיבור.",hints:["איזה key ב-routes מצביע על depot?","השוו depot_id משני הצדדים.","הכלי שמחזיר matching rows נקרא INNER JOIN."],solution:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",principle:"ה־cardinality מתארת `depots 1:M routes`; ה־Grain נשאר route כי כל row בתוצאה מייצגת route אחת."},'''

new_stage1='''{title:"איפה יצא כל מסלול?",short:"מסלולים לפי depot",eye:"חיבור מידע · לחשוב לפני התחביר",joinViz:"inner",context:"חדר הבקרה רוצה יומן מסלולים שמוסיף לכל route את האתר שממנו יצא.",task:"בנו רשימה של כל מסלול עם שם ה-depot, תאריך השירות, הסטטוס והמרחק.",output:"depot_name, route_code, service_date, status, distance_km · מיון לפי route_id.",pred:"עובדים צעד-צעד: Grain → cardinality → תפקיד ה-relation → השפעה על rows.",predQuiz:[{q:"מה ה-output Grain?",opts:[["depot","depot"],["route","route"],["vehicle","vehicle"],["stop","stop"]],ans:"route",why:"כל row בתוצאה צריכה לייצג route אחת; פרטי ה-depot רק מתווספים אליה."},{q:"מתוך route אחת, כמה rows ב-depots יכולות להתאים דרך routes.depot_id?",opts:[["zero","0"],["one","1"],["many","many"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"one",why:"routes.depot_id הוא NOT NULL Foreign Key אל depots.depot_id, שהוא Primary Key. לכן לכל route יש match אחד ב-depots."},{q:"למה בכלל צריך את depots במשימה הזאת?",opts:[["attributes","כדי להוסיף depot_name ל-row של כל route"],["existence","רק כדי לבדוק אם depot קיים"],["metric","כדי להביא rows למדד"],["preserve","כדי לשמור depots שאין להם route"]],ans:"attributes",why:"depot_name נדרש בפלט עצמו, ולכן depots צריכה לתרום attribute ל-row של route."},{q:"אם לכל route יש match אחד ב-depots, מה החיבור אמור לעשות ל-Grain ולמספר ה-rows?",opts:[["same","לשמור Grain של route ולא להכפיל rows"],["multiply","להכפיל routes"],["drop","להוריד routes"],["aggregate","לאגד כמה routes ל-row אחת"]],ans:"same",why:"match יחיד מוסיף attributes ל-route קיימת. הוא לא מפצל אותה, ולכן ה-Grain נשאר route."}],lesson:"מה-Grain מסתכלים החוצה: route → depot הוא match יחיד. כש-relation נוספת רק מוסיפה attributes דרך match יחיד, אין סיבה שה-Grain יהפוך ליותר מפורט.",operation:{"mode":"guided","tool":"INNER JOIN","model":"routes.depot_id הוא NOT NULL Foreign Key אל depots.depot_id. כבר קבענו שה-Grain הוא route וש-depots צריכה לתרום depot_name.","need":"עכשיו צריך לבחור פעולה שמצרפת לכל route את ה-depot היחיד שאליו היא מצביעה.","q":"איזו פעולה מתאימה לצירוף matching row מ-depots אל כל route?","opts":[["inner","INNER JOIN"],["exists","EXISTS"],["left","LEFT OUTER JOIN"],["group","GROUP BY"]],"ans":"inner","why":"צריך attributes מה-row התואמת ב-depots, ולפי הסכמה לכל route יש depot תואם אחד. INNER JOIN מבטא ישירות את החיבור הזה.","hint":"אנחנו צריכים את depot_name בתוך הפלט, לא רק תשובת כן/לא.","alt":"Correlated subquery יכולה להביא את depot_name, אבל JOIN מציג את הקשר בין ה-relations בצורה ישירה."},sanity:{"baselineSql":"SELECT COUNT(*) AS route_count FROM routes;","q":"הרצתם baseline על routes. אחרי החיבור, אם ההיגיון שלנו נכון, איך מספר ה-rows אמור להיות ביחס ל-baseline שראיתם?","opts":[["same","אותו מספר rows"],["more","יותר rows"],["less","פחות rows"],["unknown","אי אפשר לצפות"]],"ans":"same","why":"ה-Grain הוא route ולכל route יש match אחד ב-depots, ולכן החיבור לא אמור להכפיל או להעלים routes.","after":"השוו את מספר ה-rows של פתרון ה-JOIN ל-baseline שקיבלתם בעורך החקירה. הם צריכים להיות זהים; אם לא, בדקו את תנאי החיבור."},altSolutions:[{"label":"Correlated subquery","sql":"SELECT (SELECT d.depot_name FROM depots d WHERE d.depot_id=r.depot_id) AS depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM routes r ORDER BY r.route_id;"}],starter:"",expected:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",note:"קבעו Grain ו-cardinality לפני בחירת הפעולה.",hints:["איזה key ב-routes מצביע על depot?","השוו depot_id משני הצדדים.","אחרי שהבנתם שצריך attributes מה-match, חשבו על JOIN."],solution:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",principle:"Grain קודם ל-JOIN: route → depot הוא match יחיד, ולכן צירוף attributes מה-depot שומר על Grain של route."},'''
replace_once(old_stage1,new_stage1,'stage1 object')

# Persist a separate exploration editor state; no other stage uses it.
replace_once(
'''const defaults=()=>({version:APP_STATE_VERSION,stage:0,sql:{},notes:{},scratch:{},predAnswers:{},predChecked:{},sanityAnswers:{},sanityChecked:{},operationAnswers:{},operationChecked:{},operationHints:{},operationOpen:{},outputOpen:{},completed:[],skipped:[],hint:{},solution:{},solutionChoice:{},decision:{},structured:{grain:{},card:{}},theme:'light',attempted:[],graphOpen:{},previewRows:{},scaffoldAnswers:{},scaffoldChecked:{},checkFailures:{},skeletonOpen:{}});''',
'''const defaults=()=>({version:APP_STATE_VERSION,stage:0,sql:{},exploreSql:{},exploreRan:{},notes:{},scratch:{},predAnswers:{},predChecked:{},sanityAnswers:{},sanityChecked:{},operationAnswers:{},operationChecked:{},operationHints:{},operationOpen:{},outputOpen:{},completed:[],skipped:[],hint:{},solution:{},solutionChoice:{},decision:{},structured:{grain:{},card:{}},theme:'light',attempted:[],graphOpen:{},previewRows:{},scaffoldAnswers:{},scaffoldChecked:{},checkFailures:{},skeletonOpen:{}});''',
'default state')

replace_once(
''' out.scaffoldAnswers=out.scaffoldAnswers||{};\n out.scaffoldChecked=out.scaffoldChecked||{};''',
''' out.exploreSql=out.exploreSql||{};\n out.exploreRan=out.exploreRan||{};\n out.scaffoldAnswers=out.scaffoldAnswers||{};\n out.scaffoldChecked=out.scaffoldChecked||{};''',
'migrate exploration state')

replace_once(
'''let lastResult=null,lastError='',feedback='',queryFeedback='';\nlet cm=null;''',
'''let lastResult=null,lastError='',feedback='',queryFeedback='';\nlet exploreResult=null,exploreError='';\nlet cm=null;''',
'exploration globals')

# Schema insertion targets the exploration textarea while the solution editor is intentionally not shown yet.
replace_once(
''' const ta=document.getElementById('sql');\n if(ta){\n   const start=Number.isInteger(ta.selectionStart)?ta.selectionStart:ta.value.length;\n   const end=Number.isInteger(ta.selectionEnd)?ta.selectionEnd:start;\n   ta.value=ta.value.slice(0,start)+token+ta.value.slice(end);\n   ta.selectionStart=ta.selectionEnd=start+token.length;\n   state.sql[state.stage]=ta.value;\n   save();\n   ta.focus();\n   showInsertToast(token);\n }''',
''' const ta=document.getElementById('sql')||(state.stage===1?document.getElementById('exploreSql'):null);\n if(ta){\n   const start=Number.isInteger(ta.selectionStart)?ta.selectionStart:ta.value.length;\n   const end=Number.isInteger(ta.selectionEnd)?ta.selectionEnd:start;\n   ta.value=ta.value.slice(0,start)+token+ta.value.slice(end);\n   ta.selectionStart=ta.selectionEnd=start+token.length;\n   if(ta.id==='exploreSql')state.exploreSql[state.stage]=ta.value;else state.sql[state.stage]=ta.value;\n   save();\n   ta.focus();\n   showInsertToast(token);\n }''',
'insert target')

# The Stage 1 reasoning quiz reveals one question at a time and only advances on a correct checked answer.
replace_once(
'''function predQuestionChecked(stage,qi){\n const v=(state.predChecked||{})[stage];\n if(v===true)return true; // compatibility with v12, where the whole quiz was checked at once\n return !!(v&&typeof v==='object'&&v[qi]);\n}\nfunction predictionQuizHtml(s){''',
'''function predQuestionChecked(stage,qi){\n const v=(state.predChecked||{})[stage];\n if(v===true)return true; // compatibility with v12, where the whole quiz was checked at once\n return !!(v&&typeof v==='object'&&v[qi]);\n}\nfunction predQuestionResolved(stage,s,qi){\n const a=(state.predAnswers||{})[stage]||{};\n return predQuestionChecked(stage,qi)&&a[qi]===s.predQuiz[qi].ans;\n}\nfunction stage1ReasoningResolved(s){\n return state.stage===1&&Array.isArray(s.predQuiz)&&s.predQuiz.every((_,qi)=>predQuestionResolved(1,s,qi));\n}\nfunction stage1SanityResolved(s){\n return state.stage===1&&!!(s.sanity&&state.sanityChecked[1]&&state.sanityAnswers[1]===s.sanity.ans);\n}\nfunction predictionQuizHtml(s){''',
'stage1 reasoning helpers')

replace_once(
''' const qs=s.predQuiz.map((q,qi)=>{\n   const cur=byStage[qi]||'';''',
''' const qs=s.predQuiz.map((q,qi)=>{\n   if(state.stage===1&&qi>0&&!predQuestionResolved(1,s,qi-1))return '';\n   const cur=byStage[qi]||'';''',
'progressive stage1 quiz')

replace_once(
''' const attemptedPred=s.predQuiz?s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi)):(s.requireNote?noteStarted:true);''',
''' const attemptedPred=s.predQuiz?(state.stage===1?stage1ReasoningResolved(s):s.predQuiz.every((_,qi)=>predQuestionChecked(state.stage,qi))):(s.requireNote?noteStarted:true);''',
'stage1 model reveal')

# Stage 1 operation selection is a required visible step, not optional help.
replace_once(
''' return '<details class=\"card operation-card operation-help\" id=\"operationHelp\" '+(open?'open':'')+'><summary>לא בטוח איזו פעולה מתאימה?</summary><div class=\"operation-help-inner\">'+body+'</div></details>';''',
''' if(state.stage===1)return '<section class=\"card operation-card\"><div class=\"operation-title\">בחירת הפעולה</div>'+body+'</section>';\n return '<details class=\"card operation-card operation-help\" id=\"operationHelp\" '+(open?'open':'')+'><summary>לא בטוח איזו פעולה מתאימה?</summary><div class=\"operation-help-inner\">'+body+'</div></details>';''',
'stage1 operation card')

# Stage 1 has a real exploration editor for the baseline; the number itself is never embedded in the lesson.
replace_once(
''' const baselineHelp=spec.baselineSql?'<details class=\"sanity-sql-help\"><summary>איך מוצאים את ה־baseline ב־SQL?</summary><pre>'+esc(spec.baselineSql)+'</pre></details>':'';''',
''' const baselineHelp=(spec.baselineSql&&state.stage!==1)?'<details class=\"sanity-sql-help\"><summary>איך מוצאים את ה־baseline ב־SQL?</summary><pre>'+esc(spec.baselineSql)+'</pre></details>:'';''',
'stage1 baseline help')

replace_once(
''' return '<section class=\"card sanity-card\" aria-label=\"Sanity Check\"><div class=\"sanity-title\">⚠ SANITY CHECK · לפני SQL</div><p><b>בדיקת ציפייה: </b>'+mixedInlineHtml(spec.q)+'</p>'+baselineHelp+'<div class=\"sanity-quiz\"><select id=\"sanityAnswer\"><option value=\"\">בחרו...</option>'+spec.opts.map(o=>'<option value=\"'+esc(o[0])+'\" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><button class=\"sanity-check-btn\" id=\"checkSanity\">✓ בדוק ציפייה</button></div>'+fb+'</section>';\n}\n\nfunction sqlSupportHtml''',
''' const sanityTitle=state.stage===1?'⚠ SANITY CHECK · לפני החיבור':'⚠ SANITY CHECK · לפני SQL';\n return '<section class=\"card sanity-card\" aria-label=\"Sanity Check\"><div class=\"sanity-title\">'+sanityTitle+'</div><p><b>בדיקת ציפייה: </b>'+mixedInlineHtml(spec.q)+'</p>'+baselineHelp+'<div class=\"sanity-quiz\"><select id=\"sanityAnswer\"><option value=\"\">בחרו...</option>'+spec.opts.map(o=>'<option value=\"'+esc(o[0])+'\" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><button class=\"sanity-check-btn\" id=\"checkSanity\">✓ בדוק ציפייה</button></div>'+fb+'</section>';\n}\n\nfunction stage1ExplorationHtml(s){\n if(state.stage!==1||!stage1ReasoningResolved(s))return '';\n const sql=(state.exploreSql||{})[1]||s.sanity.baselineSql||'';\n const result=exploreResult?'<section class=\"card result explore-result\"><div class=\"resulthead\"><b>תוצאת החקירה</b><span>'+exploreResult.values.length+' rows</span></div>'+resultHtml(exploreResult)+'</section>':'';\n const err=exploreError?'<div class=\"feedback bad\">'+esc(exploreError)+'</div>':'';\n return '<section class=\"editor exploration-editor\"><div class=\"editorhead\"><b>SQL לחקירה · baseline</b><span>לא נבדק כפתרון ולא משפיע על ההתקדמות</span></div><div class=\"explore-note\">בדקו בעצמכם כמה rows יש ב-routes. השאילתה מוכנה; הריצו אותה וקראו את התוצאה.</div><textarea id=\"exploreSql\" spellcheck=\"false\">'+esc(sql)+'</textarea><div class=\"editorfoot\"><span>זהו אזור חקירה. אפשר לשנות את השאילתה ולנסות דברים.</span><div class=\"editor-buttons\"><button class=\"run\" id=\"runExplore\" '+(!db?'disabled':'')+'>▶ הרץ לחקירה</button></div></div></section>'+result+err;\n}\nfunction stage1GuidedFlowHtml(s){\n if(state.stage!==1)return '';\n let out='';\n if(stage1ReasoningResolved(s))out+=stage1ExplorationHtml(s);\n if((state.exploreRan||{})[1])out+=sanityHtml(s,false);\n if(stage1SanityResolved(s))out+=operationHtml(s)+joinVizDisclosureHtml(s);\n return out;\n}\nfunction runStage1Explore(){\n const ta=document.getElementById('exploreSql');\n const val=ta?ta.value:'';\n state.exploreSql[1]=val;\n if(!/\\bCOUNT\\s*\\(\\s*\\*\\s*\\)/i.test(val)||!/\\bFROM\\s+routes\\b/i.test(val)){\n   exploreResult=null;exploreError='בשלב הזה המטרה היא למצוא baseline: הריצו COUNT(*) על routes.';state.exploreRan[1]=false;save();render();return;\n }\n try{exploreResult=exec(val);exploreError='';state.exploreRan[1]=true;}\n catch(e){exploreResult=null;exploreError=friendlySqlError(e.message,val,1);state.exploreRan[1]=false;}\n save();render();\n}\n\nfunction sqlSupportHtml''',
'exploration editor and guided flow')

# Reuse editor styling for the exploration textarea.
replace_once(
'''#sql{width:100%;min-height:260px;border:0;outline:0;resize:vertical;background:transparent;color:#e8f0eb;padding:20px;font:13px/1.8 Consolas,monospace;direction:ltr;text-align:left}.editor-buttons''',
'''#sql,#exploreSql{width:100%;min-height:260px;border:0;outline:0;resize:vertical;background:transparent;color:#e8f0eb;padding:20px;font:13px/1.8 Consolas,monospace;direction:ltr;text-align:left}#exploreSql{min-height:150px}.explore-note{padding:12px 16px;background:rgba(255,255,255,.04);color:#c8d5ce;font-size:12px;line-height:1.65}.exploration-editor{border-color:#385b4d}.editor-buttons''',
'exploration editor css')

# Stage 1 gets its own ordered flow. Other stages keep the old rendering path byte-for-byte.
replace_once(
''' scratchHtml(s)+\n operationHtml(s)+\n joinVizDisclosureHtml(s)+\n sanityHtml(s,false)+\n scaffoldHtml(s)+''',
''' scratchHtml(s)+\n (state.stage===1?stage1GuidedFlowHtml(s):(operationHtml(s)+joinVizDisclosureHtml(s)+sanityHtml(s,false)))+\n scaffoldHtml(s)+''',
'stage1 render flow')

replace_once(
''' ((s.summary||s.intro||!scaffoldComplete(s))?'':'<section class=\"editor\"><div class=\"editorhead\"><b>SQL editor · אתם כותבים ומריצים</b><span>'+dbStatus+'</span></div>''',
''' ((s.summary||s.intro||!scaffoldComplete(s)||(state.stage===1&&!operationChoiceResolved(s)))?'':'<section class=\"editor\"><div class=\"editorhead\"><b>'+(state.stage===1?'SQL לפתרון המשימה':'SQL editor · אתם כותבים ומריצים')+'</b><span>'+dbStatus+'</span></div>''',
'stage1 solution editor gate')

# Bind the exploration editor without touching the solution checker.
replace_once(
''' const scratch=document.getElementById('scratch');\n if(scratch)scratch.oninput=()=>{state.scratch[state.stage]=scratch.value;save();};\n const sanityAnswer=document.getElementById('sanityAnswer');''',
''' const scratch=document.getElementById('scratch');\n if(scratch)scratch.oninput=()=>{state.scratch[state.stage]=scratch.value;save();};\n const exploreSql=document.getElementById('exploreSql');\n if(exploreSql){\n   exploreSql.oninput=()=>{state.exploreSql[1]=exploreSql.value;save();};\n   exploreSql.onkeydown=e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();runStage1Explore();}};\n }\n const runExplore=document.getElementById('runExplore');\n if(runExplore)runExplore.onclick=runStage1Explore;\n const sanityAnswer=document.getElementById('sanityAnswer');''',
'exploration bind')

replace_once(
'''delete state.sql[state.stage];delete state.notes[state.stage];delete state.scratch[state.stage];''',
'''delete state.sql[state.stage];delete state.exploreSql[state.stage];delete state.exploreRan[state.stage];delete state.notes[state.stage];delete state.scratch[state.stage];''',
'clear exploration state')

replace_once(
'''function clearTransient(){lastResult=null;lastError='';feedback='';queryFeedback='';}''',
'''function clearTransient(){lastResult=null;lastError='';feedback='';queryFeedback='';exploreResult=null;exploreError='';}''',
'clear exploration result')

# Guardrails: Stage 2 content unchanged, no Stage 1 baseline answer hard-coded, expected solution unchanged.
start2_after=s.index(stage2_marker)
end2_after=s.index(stage3_marker,start2_after)
if s[start2_after:end2_after] != stage2_before:
    raise SystemExit('Stage 2 object changed unexpectedly')
if 'Baseline: ב־`routes` יש 13 rows' in s[s.index('{title:"איפה יצא כל מסלול?"'):start2_after]:
    raise SystemExit('Stage 1 still leaks baseline count')
for marker in ['SQL לחקירה · baseline','stage1GuidedFlowHtml','מה ה-output Grain?','מתוך route אחת, כמה rows ב-depots','למה בכלל צריך את depots','מה החיבור אמור לעשות ל-Grain']:
    if marker not in s:
        raise SystemExit(f'missing marker: {marker}')

p.write_text(s,encoding='utf-8')
print('Stage 1 patch applied')
