from pathlib import Path

p = Path('sql-lab/index.html')
s = p.read_text(encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

old_flow = '''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=stage1BaselineSanityHtml(s)+operationHtml(s);
 if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}'''
new_flow = '''function stage1BaselinePromptHtml(){
 return '<section class="card sanity-card stage1-baseline-check" aria-label="Sanity Check"><div class="sanity-title">⚠ SANITY CHECK · לפני החיבור</div><p><b>בדיקת baseline:</b> השתמשו בעורך ה-SQL למטה כדי לבדוק כמה rows יש ב-routes. הריצו <span class="inline-ltr">SELECT COUNT(*) FROM routes;</span> — המספר שתקבלו יהיה נקודת הבקרה להשוואה אחרי ה-JOIN.</p></section>';
}
function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out='';
 if(!((state.exploreRan||{})[1]))out+=stage1BaselinePromptHtml();
 else out+=stage1BaselineSanityHtml(s)+operationHtml(s);
 if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}'''
s = replace_once(s, old_flow, new_flow, 'stage1 guided flow')

s = replace_once(s, "const shown=n===null?'נמדד באזור החקירה':('<span class=\"baseline-number\">'+n+' rows</span>');", "const shown=n===null?'נמדד בעורך ה-SQL':('<span class=\"baseline-number\">'+n+' rows</span>');", 'baseline source wording')
s = replace_once(s, 'אין כאן עוד תחזית חדשה — רק מדידה של התחזית שכבר קבענו ב-Effect.', 'זו המדידה שאליה נשווה את תוצאת ה-JOIN.', 'baseline copy')
s = replace_once(s, '(state.stage===1&&!operationChoiceResolved(s))', '(state.stage===1&&!stage1ReasoningResolved(s))', 'stage1 editor gate')
s = replace_once(s, "<div class=\"editorhead\"><b>'+(state.stage===1?'SQL לפתרון המשימה':'SQL editor · אתם כותבים ומריצים')+'</b><span>", "<div class=\"editorhead\"><b>SQL editor · אתם כותבים ומריצים</b><span>", 'editor heading')

old_buttons = "<button class=\"run\" id=\"run\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה כדי לחקור את התוצאה. אם מסומן SQL, יורץ רק הטקסט המסומן.\">▶ הרץ וחקור</button><button class=\"checkquery\" id=\"checkQuery\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה ובודק אותה מול דרישות התרגיל. אין צורך ללחוץ קודם על הרץ.\">✓ בדוק תשובה</button>"
new_buttons = "<button class=\"run\" id=\"run\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה כדי לחקור את התוצאה. אם מסומן SQL, יורץ רק הטקסט המסומן.\">▶ הרץ וחקור</button>'+((state.stage===1&&!operationChoiceResolved(s))?'':'<button class=\"checkquery\" id=\"checkQuery\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה ובודק אותה מול דרישות התרגיל. אין צורך ללחוץ קודם על הרץ.\">✓ בדוק תשובה</button>')"
s = replace_once(s, old_buttons, new_buttons, 'stage1 check-answer gate')

run_start = s.index('function runCurrent(){')
run_end = s.index('function clearTransient(){', run_start)
run_block = s[run_start:run_end]
old_exec = "try{lastResult=exec(val);lastError='';queryFeedback='';}\n catch(e){lastResult=null;lastError=friendlySqlError(e.message,val,state.stage);queryFeedback='';}"
new_exec = """try{
   lastResult=exec(val);lastError='';queryFeedback='';
   if(state.stage===1&&/^\\s*SELECT\\s+COUNT\\s*\\(\\s*\\*\\s*\\)(?:\\s+AS\\s+[A-Za-z_][A-Za-z0-9_]*)?\\s+FROM\\s+routes\\s*;?\\s*$/i.test(val)){
     const n=Number(lastResult&&lastResult.values&&lastResult.values[0]&&lastResult.values[0][0]);
     if(Number.isFinite(n)){
       state.exploreRan[1]=true;
       state.stage1BaselineCount=n;
       save();
     }
   }
 }
 catch(e){lastResult=null;lastError=friendlySqlError(e.message,val,state.stage);queryFeedback='';}"""
run_block = replace_once(run_block, old_exec, new_exec, 'runCurrent baseline detection')
s = s[:run_start] + run_block + s[run_end:]

s = replace_once(s, "if(checkOperation)checkOperation.onclick=()=>{state.operationChecked[state.stage]=true;save();render();};", "if(checkOperation)checkOperation.onclick=()=>{state.operationChecked[state.stage]=true;if(state.stage===1&&state.operationAnswers[1]===curr().operation.ans)invalidateResult();save();render();};", 'clear baseline result after operation')

old_verify = "(lastResult&&s.sanity?(state.stage===1?stage1FinalSanityHtml(s):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')"
new_verify = "(lastResult&&s.sanity?(state.stage===1?(operationChoiceResolved(s)?stage1FinalSanityHtml(s):''):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')"
s = replace_once(s, old_verify, new_verify, 'stage1 final sanity gate')

p.write_text(s, encoding='utf-8')

out = p.read_text(encoding='utf-8')
required = [
    'function stage1BaselinePromptHtml()',
    'SELECT COUNT(*) FROM routes;',
    'state.stage===1&&!stage1ReasoningResolved(s)',
    'state.exploreRan[1]=true',
    'state.stage1BaselineCount=n',
    "operationChoiceResolved(s)?stage1FinalSanityHtml(s):''",
    'eye:"מסלול → רכב · קשר M→1"',
    'renderQ(1,stage4RelationsHtml())',
    "renderQ(2,'<div class=\"stage1-concept-note\"><p>לכל route יש match אחד בדיוק ב-vehicles.</p></div>')",
    'אם ל-depot יש 3 drivers ו-3 routes, כמה rows ייווצרו בחיבור גולמי של שני ענפי ה-M?'
]
for marker in required:
    if marker not in out:
        raise SystemExit(f'missing required marker: {marker}')

flow = out[out.index('function stage1GuidedFlowHtml(s){'):out.index('function stage2GuidedFlowHtml(s){')]
if 'stage1ExplorationHtml(s)' in flow:
    raise SystemExit('Stage 1 still renders the dedicated exploration editor')

for forbidden in ['Transfer · מפעילים את אותה דרך חשיבה', 'ב-Riverbend Crossdock יש 3 drivers ו-3 routes']:
    if forbidden in out:
        raise SystemExit(f'forbidden learner-facing text remains: {forbidden}')
