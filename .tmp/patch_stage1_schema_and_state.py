from pathlib import Path

p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

# Add a Stage 1-only flow version marker to state.
if 'const STAGE1_FLOW_VERSION=2;' not in s:
    s=s.replace('const APP_STATE_VERSION=10;\n', 'const APP_STATE_VERSION=10;\nconst STAGE1_FLOW_VERSION=2;\n', 1)

# Ensure defaults contain only the new Stage 1 marker; preserve the global app version.
needle='skeletonOpen:{},exploreSql:{},exploreRan:{}});'
if needle in s:
    s=s.replace(needle,'skeletonOpen:{},exploreSql:{},exploreRan:{},stage1FlowVersion:STAGE1_FLOW_VERSION});',1)
elif 'stage1FlowVersion:STAGE1_FLOW_VERSION' not in s:
    raise SystemExit('defaults anchor not found')

# Migrate only Stage 1 state once, so old stored question indices cannot skip cardinality.
anchor='function migrateState(x){\n const raw=x||{};\n const out=Object.assign(defaults(),raw);'
if anchor not in s:
    raise SystemExit('migrateState anchor not found')
if 'raw.stage1FlowVersion' not in s:
    insert=anchor+'''\n if((raw.stage1FlowVersion||0)<STAGE1_FLOW_VERSION){
   out.predAnswers=out.predAnswers||{}; delete out.predAnswers[1];
   out.predChecked=out.predChecked||{}; delete out.predChecked[1];
   out.sanityAnswers=out.sanityAnswers||{}; delete out.sanityAnswers[1];
   out.sanityChecked=out.sanityChecked||{}; delete out.sanityChecked[1];
   out.operationAnswers=out.operationAnswers||{}; delete out.operationAnswers[1];
   out.operationChecked=out.operationChecked||{}; delete out.operationChecked[1];
   out.operationHints=out.operationHints||{}; delete out.operationHints[1];
   out.operationOpen=out.operationOpen||{}; delete out.operationOpen[1];
   out.exploreSql=out.exploreSql||{}; delete out.exploreSql[1];
   out.exploreRan=out.exploreRan||{}; delete out.exploreRan[1];
   out.graphOpen=out.graphOpen||{}; delete out.graphOpen[1];
   out.hint=out.hint||{}; delete out.hint[1];
   out.solution=out.solution||{}; delete out.solution[1];
   out.completed=(out.completed||[]).filter(i=>i!==1);
   out.attempted=(out.attempted||[]).filter(i=>i!==1);
   out.stage1FlowVersion=STAGE1_FLOW_VERSION;
 }'''
    s=s.replace(anchor,insert,1)

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

# Minimal Stage 1 evidence styling.
css_anchor='.answer-exp.good{background:#edf8f1;border:1px solid #bcdcc9;color:#285e43}'
if '.schema-evidence{' not in s:
    if css_anchor not in s:
        raise SystemExit('css anchor not found')
    s=s.replace(css_anchor,css_anchor+'.schema-evidence{margin:10px 0;padding:14px 16px;border:1px solid #c8d8cf;border-radius:12px;background:#f7fbf8}.schema-evidence-title{font-weight:900;margin-bottom:6px}.schema-evidence p{margin:0 0 10px;color:var(--muted);font-size:12px}.schema-evidence-grid{display:grid;grid-template-columns:max-content 1fr;gap:7px 12px;align-items:center;direction:ltr;text-align:left}.schema-evidence-grid code{font-weight:900}:root[data-theme="dark"] .schema-evidence{background:#152019;border-color:#3b5045}',1)

p.write_text(s,encoding='utf-8')
print('patched Stage 1 schema evidence and state migration')
