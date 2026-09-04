from pathlib import Path

path = Path('sql-lab/index.html')
s = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s.replace(old, new, 1)

# Stage 1 Q2: remove the artificial "Role" concept label and keep the explanation concrete.
old_q2 = '''{q:"מתוך המידע שהבקשה דורשת, איזה פריט לא נמצא ב-routes ולכן צריך להגיע מ-relation אחרת?",opts:[["depot_name","depot_name"],["route_code","route_code"],["service_date","service_date"],["distance_km","distance_km"]],ans:"depot_name",why:"route_code, service_date, status ו-distance_km כבר נמצאים ב-routes. depot_name נמצא ב-depots. לכן אנחנו צריכים את depots כדי להשלים את המידע שחסר בפלט.",concept:"Role של depots = הוספת attribute לפלט: depot_name"}'''
new_q2 = '''{q:"מתוך המידע שהבקשה דורשת, איזה פריט לא נמצא ב-routes ולכן צריך להגיע מ-relation אחרת?",opts:[["depot_name","depot_name"],["route_code","route_code"],["service_date","service_date"],["distance_km","distance_km"]],ans:"depot_name",why:"route_code, service_date, status ו-distance_km כבר נמצאים ב-routes. depot_name נמצא ב-depots. לכן צריך את depots כדי להביא את depot_name."}'''
replace_once(old_q2, new_q2, 'Stage 1 Q2')

# Stage 1 Q3: teach Cardinality and 1:M explicitly, with plain language and no "points to" wording.
old_q3 = '''{q:"עכשיו הסתכלו על הקשר בין routes ל-depots: מתוך route אחת, כמה rows ב-depots יכולות להתאים דרך depot_id?",opts:[["zero","0"],["one","1"],["many","many"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"one",why:"routes.depot_id הוא Foreign Key וגם NOT NULL. הוא מצביע על depots.depot_id, שהוא Primary Key. ה-PK מזהה row אחת בלבד, וה-NOT NULL אומר של-route חייב להיות depot_id. לכן לכל route יש match אחד ב-depots.",concept:"Cardinality: route → depot = 1 · depot → routes = 0..many (1:M)"}'''
new_q3 = '''{q:"לכל route, כמה depots יכולים להתאים?",opts:[["zero","0"],["one","1"],["many","many"],["unknown","אי אפשר לדעת מהסכמה"]],ans:"one",why:"לכל route יש depot_id שחייב להתאים ל-depot_id שקיים ב-depots. מכיוון ש-depots.depot_id הוא Primary Key, יש רק depot אחד עם אותו ערך. לכן לכל route מתאים depot אחד בדיוק. בכיוון ההפוך, depot אחד יכול להיות קשור לכמה routes.",concept:"Cardinality: הקשר depots → routes הוא 1:M — אחד לרבים."}'''
replace_once(old_q3, new_q3, 'Stage 1 Q3')

# Stage 1 Q4: keep only the consequence for the output grain; remove artificial Effect/fanout terminology.
old_q4 = '''{q:"אם לכל route מתאימה row אחת בלבד ב-depots, מה החיבור אמור לעשות ל-Grain ולמספר ה-rows?",opts:[["same","לשמור Grain של route ולא להכפיל rows"],["multiply","להכפיל routes"],["drop","להוריד routes"],["aggregate","לאגד כמה routes ל-row אחת"]],ans:"same",why:"לכל route מצטרפת row אחת בלבד של depot. לכן route לא מתפצלת לכמה rows, וה-Grain נשאר route.",concept:"Effect: ה-Grain נשאר route · מספר ה-rows נשמר · אין fanout"}'''
new_q4 = '''{q:"אם לכל route מתאים depot אחד בדיוק, מה יקרה אחרי החיבור?",opts:[["same","כל route תישאר שורה אחת"],["multiply","routes יוכפלו"],["drop","חלק מה-routes ייעלמו"],["aggregate","כמה routes יאוחדו לשורה אחת"]],ans:"same",why:"לכל route מצטרף depot אחד בלבד, ולכן כל route נשארת שורה אחת גם אחרי החיבור. ה-Grain נשאר route."}'''
replace_once(old_q4, new_q4, 'Stage 1 Q4')

# Make the concept closure read like a concept name, not a meta label.
replace_once('<div class="stage1-concept-close"><b>שם למסקנה:</b> ', '<div class="stage1-concept-close"><b>המושג:</b> ', 'Stage 1 concept label')

# Remove the repeated Stage 1 model/lesson block after Q4; Stage 2+ remains unchanged.
old_followup = ''' const followup=(model||lesson)?'<div id="predictionFollowup" class="prediction-followup '+(attemptedPred?'':'is-hidden')+'">'+model+lesson+'</div>':'';'''
new_followup = ''' const followup=state.stage===1?'':((model||lesson)?'<div id="predictionFollowup" class="prediction-followup '+(attemptedPred?'':'is-hidden')+'">'+model+lesson+'</div>':'');'''
replace_once(old_followup, new_followup, 'Stage 1 repeated followup')

# Avoid "points to" wording in the next transition as well.
replace_once('"עכשיו צריך לבחור פעולה שמצרפת לכל route את ה-depot היחיד שאליו היא מצביעה."', '"עכשיו צריך לבחור פעולה שמצרפת לכל route את ה-depot שמתאים ל-depot_id שלה."', 'Stage 1 operation transition')

# Simplify mistake-specific feedback so it matches the new wording.
replace_once("zero:'routes.depot_id הוא FK וגם NOT NULL. מה שני האילוצים האלה אומרים לגבי האפשרות שלא יהיה match?'", "zero:'ל-route יש depot_id שחייב להתאים לערך שקיים ב-depots. האם יכולה להיות route בלי depot תואם?'", 'Q3 zero feedback')
replace_once("many:'הסתכלו על depots.depot_id: הוא Primary Key. האם אותו depot_id יכול לזהות כמה rows ב-depots?'", "many:'depots.depot_id הוא Primary Key. האם אותו depot_id יכול להופיע בשתי rows שונות ב-depots?'", 'Q3 many feedback')
replace_once("unknown:'ה-schema כן נותן מספיק מידע: PK קובע ייחודיות, ו-FK + NOT NULL קובעים שהפניה חייבת להתאים.'", "unknown:'ה-schema כן נותן מספיק מידע: depot_id ב-routes חייב להתאים לערך שקיים ב-depots, ו-depots.depot_id הוא Primary Key.'", 'Q3 unknown feedback')
replace_once("drop:'INNER JOIN יכול להוריד unmatched rows באופן כללי, אבל כאן FK + NOT NULL מבטיחים שלכל route יש depot תואם.'", "drop:'כאן לכל route יש depot תואם אחד בדיוק, ולכן אין route שאמורה להיעלם.'", 'Q4 drop feedback')

path.write_text(s, encoding='utf-8')
print('patched Stage 1 wording and Cardinality teaching')
