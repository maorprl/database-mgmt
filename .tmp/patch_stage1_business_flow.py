from pathlib import Path

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

# Stage 1 flow version: reset only Stage 1 once because the question order changes.
s=s.replace('const STAGE1_FLOW_VERSION=2;','const STAGE1_FLOW_VERSION=3;',1)

# Replace only the Stage 1 definition. Keep every later stage byte-for-byte unchanged.
start=s.index('{title:"איפה יצא כל מסלול?"')
end=s.index('{title:"מי שייך לכל אתר?"', start)
new_stage='''{title:"איפה יצא כל מסלול?",short:"מסלולים לפי depot",eye:"חיבור מידע · לחשוב לפני התחביר",joinViz:"inner",context:"חדר הבקרה רוצה יומן מסלולים שמוסיף לכל route את האתר שממנו יצא.",task:"בנו רשימה של כל מסלול עם שם ה-depot, תאריך השירות, הסטטוס והמרחק.",output:"depot_name, route_code, service_date, status, distance_km · מיון לפי route_id.",pred:"מפרקים את הבקשה העסקית לחלקים: מה row מייצגת, איזה מידע חסר, איך ה-relations קשורות, ומה החיבור יעשה לתוצאה.",predQuiz:[{q:"בבקשה העסקית הזאת, מה כל row בתוצאה צריכה לייצג?",opts:[["depot","depot"],["route","route"],["vehicle","vehicle"],["stop","stop"]],ans:"route",why:"הבקשה היא רשימה של מסלולים. לכן כל row בתוצאה צריכה לייצג route אחת."},{q:"מתוך המידע שהבקשה דורשת, איזה פריט לא נמצא ב-routes ולכן צריך להגיע מ-relation אחרת?",opts:[["depot_name","depot_name"],["route_code","route_code"],["service_date","service_date"],["distance_km","distance_km"]],ans:"depot_name",why:"route_code, service_date, status ו-distance_km כבר נמצאים ב-routes. depot_name נמצא ב-depots. לכן אנחנו צריכים את depots כדי להשלים את המידע שחסר בפלט."},{q:"עכשיו הסתכלו על הקשר בין routes ל-depots: מתוך route אחת, כמה rows ב-depots יכולות להתאים דרך depot_id?",opts:[["zero","0"],["one","1"],["many","many"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"one",why:"routes.depot_id הוא Foreign Key וגם NOT NULL. הוא מצביע על depots.depot_id, שהוא Primary Key. ה-PK מזהה row אחת בלבד, וה-NOT NULL אומר של-route חייב להיות depot_id. לכן לכל route יש match אחד ב-depots."},{q:"אם לכל route מתאימה row אחת בלבד ב-depots, מה החיבור אמור לעשות ל-Grain ולמספר ה-rows?",opts:[["same","לשמור Grain של route ולא להכפיל rows"],["multiply","להכפיל routes"],["drop","להוריד routes"],["aggregate","לאגד כמה routes ל-row אחת"]],ans:"same",why:"לכל route מצטרפת row אחת בלבד של depot. לכן route לא מתפצלת לכמה rows, וה-Grain נשאר route."}],lesson:"חזרנו שוב ושוב לאותה בקשה עסקית: row אחת = route; depot_name חסר ב-routes; הקשר דרך depot_id נותן match אחד; לכן צירוף depot_name לא אמור לשנות את ה-Grain או להכפיל rows.",operation:{"mode":"guided","tool":"INNER JOIN","model":"routes.depot_id הוא NOT NULL Foreign Key אל depots.depot_id. כבר קבענו שה-Grain הוא route וש-depots צריכה לתרום depot_name.","need":"עכשיו צריך לבחור פעולה שמצרפת לכל route את ה-depot היחיד שאליו היא מצביעה.","q":"איזו פעולה מתאימה לצירוף matching row מ-depots אל כל route?","opts":[["inner","INNER JOIN"],["exists","EXISTS"],["left","LEFT OUTER JOIN"],["group","GROUP BY"]],"ans":"inner","why":"צריך attributes מה-row התואמת ב-depots, ולפי הסכמה לכל route יש depot תואם אחד. INNER JOIN מבטא ישירות את החיבור הזה.","hint":"אנחנו צריכים את depot_name בתוך הפלט, לא רק תשובת כן/לא.","alt":"Correlated subquery יכולה להביא את depot_name, אבל JOIN מציג את הקשר בין ה-relations בצורה ישירה."},sanity:{"baselineSql":"SELECT COUNT(*) AS route_count FROM routes;","q":"הרצתם baseline על routes. אחרי החיבור, אם ההיגיון שלנו נכון, איך מספר ה-rows אמור להיות ביחס ל-baseline שראיתם?","opts":[["same","אותו מספר rows"],["more","יותר rows"],["less","פחות rows"],["unknown","אי אפשר לצפות"]],"ans":"same","why":"ה-Grain הוא route ולכל route יש match אחד ב-depots, ולכן החיבור לא אמור להכפיל או להעלים routes.","after":"השוו את מספר ה-rows של פתרון ה-JOIN ל-baseline שקיבלתם בעורך החקירה. הם צריכים להיות זהים; אם לא, בדקו את תנאי החיבור."},altSolutions:[{"label":"Correlated subquery","sql":"SELECT (SELECT d.depot_name FROM depots d WHERE d.depot_id=r.depot_id) AS depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM routes r ORDER BY r.route_id;"}],starter:"",expected:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",note:"פרקו את הבקשה העסקית לפני בחירת הפעולה.",hints:["איזה key ב-routes מצביע על depot?","השוו depot_id משני הצדדים.","אחרי שהבנתם שצריך attributes מה-match, חשבו על JOIN."],solution:"SELECT d.depot_name,r.route_code,r.service_date,r.status,r.distance_km FROM depots d INNER JOIN routes r ON r.depot_id=d.depot_id ORDER BY r.route_id;",principle:"Grain קודם ל-JOIN: route → depot הוא match יחיד, ולכן צירוף attributes מה-depot שומר על Grain של route."},\n'''
s=s[:start]+new_stage+s[end:]

# Replace the old meta-style schema box with a concrete two-relation view and reading guide.
old_css='.answer-exp.good{background:#edf8f1;border:1px solid #bcdcc9;color:#285e43}.schema-evidence{margin:10px 0;padding:14px 16px;border:1px solid #c8d8cf;border-radius:12px;background:#f7fbf8}.schema-evidence-title{font-weight:900;margin-bottom:6px}.schema-evidence p{margin:0 0 10px;color:var(--muted);font-size:12px}.schema-evidence-grid{display:grid;grid-template-columns:max-content 1fr;gap:7px 12px;align-items:center;direction:ltr;text-align:left}.schema-evidence-grid code{font-weight:900}:root[data-theme="dark"] .schema-evidence{background:#152019;border-color:#3b5045}'
new_css='.answer-exp.good{background:#edf8f1;border:1px solid #bcdcc9;color:#285e43}.stage1-business-anchor{margin:0 0 16px;padding:12px 14px;border-right:4px solid var(--orange);background:#fff9f4;border-radius:10px;line-height:1.65}.stage1-business-anchor b{display:block;margin-bottom:3px}.stage1-business-anchor span{font-size:13px}.stage1-relations{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}.stage1-relation{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fafbf9}.stage1-relation h4{margin:0;padding:10px 12px;background:#f1f5f2;border-bottom:1px solid var(--line);font:900 13px Consolas,monospace;direction:ltr;text-align:left}.stage1-relation table{width:100%;min-width:0;font-size:11px}.stage1-relation th,.stage1-relation td{padding:7px 9px}.stage1-relation th{position:static}.stage1-key{font-weight:900}.stage1-key-guide{margin:12px 0;padding:12px 14px;border:1px solid #d8e2dc;border-radius:10px;background:#f7faf8;font-size:12px;line-height:1.65}.stage1-key-guide h4{margin:0 0 7px;font-size:12px}.stage1-key-guide .key-link{direction:ltr;text-align:left;font:700 12px Consolas,monospace;margin-bottom:8px}.stage1-key-guide ul{margin:0;padding-right:18px}.stage1-key-guide li{margin:3px 0}:root[data-theme="dark"] .stage1-business-anchor{background:#2a211a}:root[data-theme="dark"] .stage1-relation,:root[data-theme="dark"] .stage1-key-guide{background:#152019}:root[data-theme="dark"] .stage1-relation h4{background:#1a2820}@media(max-width:760px){.stage1-relations{grid-template-columns:1fr}}'
if old_css not in s:
    raise SystemExit('old Stage 1 schema CSS not found')
s=s.replace(old_css,new_css,1)

# Insert concrete relation/key helpers just before predictionQuizHtml.
marker='function predictionQuizHtml(s){'
if marker not in s:
    raise SystemExit('predictionQuizHtml marker not found')
helpers=r'''function stage1RelationsHtml(){
 return '<div class="stage1-relations">'+
 '<section class="stage1-relation"><h4>routes</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>route_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_id</td><td class="stage1-key">FK → depots.depot_id · NOT NULL</td></tr>'+
 '<tr><td>vehicle_id</td><td>FK → vehicles.vehicle_id · NOT NULL</td></tr>'+
 '<tr><td>route_code</td><td>UNIQUE · NOT NULL</td></tr>'+
 '<tr><td>service_date</td><td>NOT NULL</td></tr>'+
 '<tr><td>status</td><td>NOT NULL</td></tr>'+
 '<tr><td>distance_km</td><td>NOT NULL</td></tr>'+
 '</tbody></table></section>'+
 '<section class="stage1-relation"><h4>depots</h4><table><thead><tr><th>attribute</th><th>key / constraint</th></tr></thead><tbody>'+
 '<tr><td>depot_id</td><td class="stage1-key">PK</td></tr>'+
 '<tr><td>depot_name</td><td>NOT NULL</td></tr>'+
 '<tr><td>region</td><td>NOT NULL</td></tr>'+
 '<tr><td>opened_at</td><td>NOT NULL</td></tr>'+
 '</tbody></table></section></div>';
}
function stage1KeyGuideHtml(){
 return '<div class="stage1-key-guide"><h4>איך קוראים את הסימון?</h4><div class="key-link">routes.depot_id → depots.depot_id</div><ul><li><b>PK</b> מזהה row אחת באופן ייחודי.</li><li><b>FK</b> הוא attribute שמצביע ל-key ב-relation אחרת.</li><li><b>NOT NULL</b> אומר שחייב להיות ערך ב-attribute הזה.</li></ul></div>';
}
'''
s=s.replace(marker,helpers+marker,1)

# Replace only the Stage 1 branch of predictionQuizHtml: business question -> full relations -> source -> key reading -> cardinality -> effect.
start=s.index('function predictionQuizHtml(s){')
branch_start=s.index(' if(state.stage===1){',start)
branch_end=s.index(' const qs=s.predQuiz.map',branch_start)
new_branch=r''' if(state.stage===1){
   const renderQ=(qi)=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(1,qi);
     const exp=(checked&&cur)?('<div class="answer-exp '+(cur===q.ans?'good':'wrong')+'"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(q.why)+'</div>'):'';
     return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label><select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';
   };
   let out=renderQ(0);
   if(predQuestionResolved(1,s,0))out+=stage1RelationsHtml()+renderQ(1);
   if(predQuestionResolved(1,s,1))out+=stage1KeyGuideHtml()+renderQ(2);
   if(predQuestionResolved(1,s,2))out+=renderQ(3);
   return '<div class="pred-quiz">'+out+'</div>';
 }
'''
s=s[:branch_start]+new_branch+s[branch_end:]

# Keep the business request visible inside the reasoning card and use a concrete title for Stage 1.
old=" const followup=(model||lesson)?'<div id=\"predictionFollowup\" class=\"prediction-followup '+(attemptedPred?'':'is-hidden')+'\">'+model+lesson+'</div>':'';\n return '<section class=\"card relational-card\"><div class=\"relational-title\">המודל הרלציוני</div>'+quiz+followup+'</section>';"
new=" const followup=(model||lesson)?'<div id=\"predictionFollowup\" class=\"prediction-followup '+(attemptedPred?'':'is-hidden')+'\">'+model+lesson+'</div>':'';\n const stageTitle=state.stage===1?'מפרקים את הבקשה העסקית':'המודל הרלציוני';\n const businessAnchor=state.stage===1?'<div class=\"stage1-business-anchor\"><b>הבקשה העסקית</b><span>'+esc(s.task)+'</span></div>':'';\n return '<section class=\"card relational-card\"><div class=\"relational-title\">'+stageTitle+'</div>'+businessAnchor+quiz+followup+'</section>';"
if old not in s:
    raise SystemExit('relationalModelHtml return anchor not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('patched Stage 1 business-led flow')
