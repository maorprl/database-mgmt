from pathlib import Path

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

# Add a Stage 1-only flow version marker; do not bump the global app state version.
if 'const STAGE1_FLOW_VERSION=2;' not in s:
    s=s.replace('const APP_STATE_VERSION=10;\n', 'const APP_STATE_VERSION=10;\nconst STAGE1_FLOW_VERSION=2;\n', 1)

# Persist the Stage 1 flow marker in state defaults.
if 'stage1FlowVersion:STAGE1_FLOW_VERSION' not in s:
    needle='checkFailures:{},skeletonOpen:{}});'
    if needle not in s:
        raise SystemExit('defaults anchor not found')
    s=s.replace(needle,'checkFailures:{},skeletonOpen:{},stage1FlowVersion:STAGE1_FLOW_VERSION});',1)

# Migrate only Stage 1 state, after all old global-version remaps have finished.
if 'raw.stage1FlowVersion' not in s:
    anchor=" out.theme=out.theme==='dark'?'dark':'light';"
    if anchor not in s:
        raise SystemExit('migrate tail anchor not found')
    migration=''' if((raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION){
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
    s=s.replace(anchor,migration+anchor,1)

# Save the Stage 1-only migration even though APP_STATE_VERSION stays unchanged.
old=" if((raw.version||0)<APP_STATE_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));"
new=" if((raw.version||0)<APP_STATE_VERSION||(raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION)localStorage.setItem(STORAGE_KEY,JSON.stringify(out));"
if old in s:
    s=s.replace(old,new,1)
elif new not in s:
    raise SystemExit('load persistence anchor not found')

# Stage 1 renderer: explicit sequential flow + mandatory schema evidence before cardinality.
start=s.index('function predictionQuizHtml(s){')
end=s.index('function relationalModelHtml(s){',start)
new_block=r'''function predictionQuizHtml(s){
 const byStage=(state.predAnswers||{})[state.stage]||{};
 if(state.stage===1){
   const renderQ=(qi)=>{
     const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(1,qi);
     const exp=(checked&&cur)?('<div class="answer-exp '+(cur===q.ans?'good':'wrong')+'"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(q.why)+'</div>'):'';
     return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label><select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';
   };
   let out=renderQ(0);
   if(predQuestionResolved(1,s,0)){
     out+='<div class="schema-evidence"><div class="schema-evidence-title">ראיות מה־Schema · חלק מהמשימה</div><p>כדי לענות על ה־cardinality, לא מנחשים. קראו את שני ה־keys:</p><div class="schema-evidence-grid"><code>routes.depot_id</code><span>Foreign Key · NOT NULL → <code>depots.depot_id</code></span><code>depots.depot_id</code><span>Primary Key</span></div></div>';
     out+=renderQ(1);
   }
   if(predQuestionResolved(1,s,1))out+=renderQ(2);
   if(predQuestionResolved(1,s,2))out+=renderQ(3);
   return '<div class="pred-quiz">'+out+'</div>';
 }
 const qs=s.predQuiz.map((q,qi)=>{
   const cur=byStage[qi]||'';
   const checked=predQuestionChecked(state.stage,qi);
   const exp=(checked&&cur)?('<div class="answer-exp '+(cur===q.ans?'good':'wrong')+'"><b>'+(cur===q.ans?'נכון. ':'עוד לא. ')+'</b>'+esc(q.why)+'</div>'):'';
   return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label><select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+exp+'</div>';
 }).join('');
 return '<div class="pred-quiz">'+qs+'</div>';
}
'''
s=s[:start]+new_block+s[end:]

# Minimal styling for the mandatory evidence block.
css_anchor='.answer-exp.good{background:#edf8f1;border:1px solid #bcdcc9;color:#285e43}'
if '.schema-evidence{' not in s:
    if css_anchor not in s:
        raise SystemExit('css anchor not found')
    css=css_anchor+'.schema-evidence{margin:10px 0;padding:14px 16px;border:1px solid #c8d8cf;border-radius:12px;background:#f7fbf8}.schema-evidence-title{font-weight:900;margin-bottom:6px}.schema-evidence p{margin:0 0 10px;color:var(--muted);font-size:12px}.schema-evidence-grid{display:grid;grid-template-columns:max-content 1fr;gap:7px 12px;align-items:center;direction:ltr;text-align:left}.schema-evidence-grid code{font-weight:900}:root[data-theme="dark"] .schema-evidence{background:#152019;border-color:#3b5045}'
    s=s.replace(css_anchor,css,1)

p.write_text(s,encoding='utf-8')
print('patched Stage 1 schema evidence and state migration')
