from pathlib import Path

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')


def replace_once(text, old, new, label):
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {n}')
    return text.replace(old,new,1)

# Freeze course data: this patch is flow/UI only and must not alter any STAGE object.
stages_start=s.index('const STAGES=')
stages_end=s.index('const GUIDED_STAGE_META', stages_start)
stages_before=s[stages_start:stages_end]

# --- Stage 1: restore the dedicated baseline editor + separate solution editor.
# The exploration editor stays first. Running the baseline is useful but must not gate access
# to the operation-choice step.
old_flow='''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out='';
 if(!((state.exploreRan||{})[1]))out+=stage1BaselinePromptHtml();
 else out+=stage1BaselineSanityHtml(s)+operationHtml(s);
 if((state.exploreRan||{})[1]&&operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}'''
new_flow='''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=stage1BaselineSanityHtml(s);
 out+=operationHtml(s);
 if(operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);
 return out;
}'''
s=replace_once(s,old_flow,new_flow,'Stage 1 guided flow')

# Remove the one-editor-only prompt that was introduced by mistake.
start=s.index('function stage1BaselinePromptHtml(){')
end=s.index('function stage1GuidedFlowHtml(s){',start)
s=s[:start]+s[end:]

# Keep the exploration editor genuinely exploratory: any read-only SQL can run.
# If the learner does run the baseline COUNT, remember it for the later comparison,
# but do not make that recognition a prerequisite for continuing.
old_explore='''function runStage1Explore(){
 const ta=document.getElementById('exploreSql');
 const val=ta?ta.value:'';
 state.exploreSql[1]=val;
 if(!/\\bCOUNT\\s*\\(\\s*\\*\\s*\\)/i.test(val)||!/\\bFROM\\s+routes\\b/i.test(val)){
   exploreResult=null;exploreError='בשלב הזה המטרה היא למצוא baseline: הריצו COUNT(*) על routes.';state.exploreRan[1]=false;save();render();return;
 }
 try{
   exploreResult=exec(val);exploreError='';state.exploreRan[1]=true;
   const n=Number(exploreResult&&exploreResult.values&&exploreResult.values[0]&&exploreResult.values[0][0]);
   if(Number.isFinite(n))state.stage1BaselineCount=n;
 }
 catch(e){exploreResult=null;exploreError=friendlySqlError(e.message,val,1);state.exploreRan[1]=false;}
 save();render();
}'''
new_explore='''function runStage1Explore(){
 const ta=document.getElementById('exploreSql');
 const val=ta?ta.value:'';
 state.exploreSql[1]=val;
 if(!val.trim()){exploreResult=null;exploreError='כתבו שאילתת SQL לפני ההרצה.';save();render();return;}
 try{
   exploreResult=exec(val);exploreError='';
   if(/^\\s*SELECT\\s+COUNT\\s*\\(\\s*\\*\\s*\\)(?:\\s+AS\\s+[A-Za-z_][A-Za-z0-9_]*)?\\s+FROM\\s+routes\\s*;?\\s*$/i.test(val)){
     const n=Number(exploreResult&&exploreResult.values&&exploreResult.values[0]&&exploreResult.values[0][0]);
     if(Number.isFinite(n)){
       state.exploreRan[1]=true;
       state.stage1BaselineCount=n;
     }
   }
 }
 catch(e){exploreResult=null;exploreError=friendlySqlError(e.message,val,1);}
 save();render();
}'''
s=replace_once(s,old_explore,new_explore,'Stage 1 exploration runner')

# Clean the baseline confirmation copy left by the one-editor patch.
s=replace_once(
    s,
    "return '<section class=\"card sanity-card stage1-baseline-check\" aria-label=\"Sanity Check\"><div class=\"sanity-title\">✓ SANITY CHECK · baseline נמדד</div><p><b>נקודת הבקרה:</b> ב-routes יש '+shown+'. זה המספר שאליו נשווה את תוצאת ה-JOIN. זו המדידה שאליה נשווה את תוצאת ה-JOIN.</p></section>';",
    "return '<section class=\"card sanity-card stage1-baseline-check\" aria-label=\"Sanity Check\"><div class=\"sanity-title\">✓ SANITY CHECK · baseline נמדד</div><p><b>נקודת הבקרה:</b> ב-routes יש '+shown+'. זה המספר שאליו נשווה את תוצאת ה-JOIN.</p></section>';",
    'Stage 1 baseline copy'
)

# Restore the second/main SQL editor as a separate solution editor, unlocked by the
# operation choice — not by the baseline query.
s=replace_once(s,'(state.stage===1&&!stage1ReasoningResolved(s))','(state.stage===1&&!operationChoiceResolved(s))','Stage 1 solution-editor gate')
s=replace_once(
    s,
    '<div class="editorhead"><b>SQL editor · אתם כותבים ומריצים</b><span>',
    '<div class="editorhead"><b>\'+(state.stage===1?\'SQL לפתרון המשימה\':\'SQL editor · אתם כותבים ומריצים\')+\'</b><span>',
    'Stage 1 solution-editor heading'
)

old_check_button="<button class=\"run\" id=\"run\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה כדי לחקור את התוצאה. אם מסומן SQL, יורץ רק הטקסט המסומן.\">▶ הרץ וחקור</button>'+((state.stage===1&&!operationChoiceResolved(s))?'':'<button class=\"checkquery\" id=\"checkQuery\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה ובודק אותה מול דרישות התרגיל. אין צורך ללחוץ קודם על הרץ.\">✓ בדוק תשובה</button>')"
new_check_button="<button class=\"run\" id=\"run\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה כדי לחקור את התוצאה. אם מסומן SQL, יורץ רק הטקסט המסומן.\">▶ הרץ וחקור</button><button class=\"checkquery\" id=\"checkQuery\" '+(!db?'disabled':'')+' title=\"מריץ את השאילתה ובודק אותה מול דרישות התרגיל. אין צורך ללחוץ קודם על הרץ.\">✓ בדוק תשובה</button>"
s=replace_once(s,old_check_button,new_check_button,'Stage 1 solution-editor buttons')

# The main solution editor must no longer double as the baseline editor.
old_run=''' try{
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
 catch(e){lastResult=null;lastError=friendlySqlError(e.message,val,state.stage);queryFeedback='';}'''
new_run=""" try{lastResult=exec(val);lastError='';queryFeedback='';}
 catch(e){lastResult=null;lastError=friendlySqlError(e.message,val,state.stage);queryFeedback='';}"""
s=replace_once(s,old_run,new_run,'main editor baseline side effect')

s=replace_once(
    s,
    "if(checkOperation)checkOperation.onclick=()=>{state.operationChecked[state.stage]=true;if(state.stage===1&&state.operationAnswers[1]===curr().operation.ans)invalidateResult();save();render();};",
    "if(checkOperation)checkOperation.onclick=()=>{state.operationChecked[state.stage]=true;save();render();};",
    'Stage 1 operation handler'
)

s=replace_once(
    s,
    "(lastResult&&s.sanity?(state.stage===1?(operationChoiceResolved(s)?stage1FinalSanityHtml(s):''):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')",
    "(lastResult&&s.sanity?(state.stage===1?stage1FinalSanityHtml(s):'<div class=\"result-verify\"><b>Verify:</b> '+mixedInlineHtml(s.sanity.after)+'</div>'):'')",
    'Stage 1 final sanity rendering'
)

# --- Stage 3: question first, then the evidence needed to answer it, then choices.
s=replace_once(
    s,
    'if(predQuestionResolved(3,s,1))out+=stage3RelationsHtml()+stage3KeyGuideHtml()+renderQ(2);',
    'if(predQuestionResolved(3,s,1))out+=renderQ(2,stage3RelationsHtml()+stage3KeyGuideHtml());',
    'Stage 3 key/schema placement'
)
s=replace_once(
    s,
    'if(predQuestionResolved(3,s,2))out+=stage3CardinalityMapHtml()+renderQ(3);',
    'if(predQuestionResolved(3,s,2))out+=renderQ(3,stage3CardinalityMapHtml());',
    'Stage 3 cardinality placement'
)

# Acceptance checks.
out=s
if out[stages_start:stages_start+len(stages_before)] != stages_before:
    raise SystemExit('STAGES data changed; scope violation')

required=[
    'let out=stage1ExplorationHtml(s);',
    'out+=operationHtml(s);',
    'if(operationChoiceResolved(s))out+=stage1JoinPredicateHtml()+joinVizDisclosureHtml(s);',
    '<b>SQL לחקירה · baseline</b>',
    '<b>\'+(state.stage===1?\'SQL לפתרון המשימה\':\'SQL editor · אתם כותבים ומריצים\')+\'</b>',
    '(state.stage===1&&!operationChoiceResolved(s))',
    'function runStage1Explore(){',
    "if(!val.trim()){exploreResult=null;exploreError='כתבו שאילתת SQL לפני ההרצה.'",
    'renderQ(2,stage3RelationsHtml()+stage3KeyGuideHtml())',
    'renderQ(3,stage3CardinalityMapHtml())',
    'eye:"מסלול → רכב · קשר M→1"',
    'renderQ(1,stage4RelationsHtml())',
    "renderQ(2,'<div class=\"stage1-concept-note\"><p>לכל route יש match אחד בדיוק ב-vehicles.</p></div>')",
    'אם ל-depot יש 3 drivers ו-3 routes, כמה rows ייווצרו בחיבור גולמי של שני ענפי ה-M?'
]
for marker in required:
    if marker not in out:
        raise SystemExit(f'missing required marker: {marker}')

for forbidden in [
    'function stage1BaselinePromptHtml()',
    "if(!/\\bCOUNT\\s*\\(\\s*\\*\\s*\\)/i.test(val)||!/\\bFROM\\s+routes\\b/i.test(val))",
    'Transfer · מפעילים את אותה דרך חשיבה',
    'ב-Riverbend Crossdock יש 3 drivers ו-3 routes'
]:
    if forbidden in out:
        raise SystemExit(f'forbidden marker remains: {forbidden}')

# Explicitly preserve Stage 2 flow and all stage data; no Stage 5+ behavior is touched by
# the Stage-specific replacements above.
p.write_text(out,encoding='utf-8')
