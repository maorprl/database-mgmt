from pathlib import Path
p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if s.count(old)!=1:
        raise SystemExit(f'{label}: expected one match, got {s.count(old)}')
    s=s.replace(old,new,1)

rep(
'''function relationGraphUnlocked(){return true;}''',
'''function relationGraphUnlocked(){
 if(state.stage!==1)return true;
 return (state.attempted||[]).includes(1)||state.hint[1]!==undefined||!!state.operationHints[1];
}''',
'stage1 relation graph gate')

rep(
'''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 let out='';
 if(stage1ReasoningResolved(s))out+=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=sanityHtml(s,false);
 if(stage1SanityResolved(s))out+=operationHtml(s)+joinVizDisclosureHtml(s);
 return out;
}''',
'''function stage1GuidedFlowHtml(s){
 if(state.stage!==1)return '';
 if(!stage1ReasoningResolved(s))return '';
 let out=stage1ExplorationHtml(s);
 if((state.exploreRan||{})[1])out+=sanityHtml(s,false);
 if((state.exploreRan||{})[1]&&stage1SanityResolved(s))out+=operationHtml(s)+joinVizDisclosureHtml(s);
 return out;
}''',
'stage1 nested flow')

rep(
''' let out='<section class="sql-support"><div class="support-actions"><button class="hintbtn" id="hint">רמז</button><button class="solutionbtn" id="solution">פתרונות</button><button class="clearbtn" id="clearStage">נקה שלב</button></div>';''',
''' const allowFullSolution=state.stage!==1||(state.attempted||[]).includes(1);
 let out='<section class="sql-support"><div class="support-actions"><button class="hintbtn" id="hint">רמז</button>'+(allowFullSolution?'<button class="solutionbtn" id="solution">פתרונות</button>':'')+'<button class="clearbtn" id="clearStage">נקה שלב</button></div>';''',
'stage1 solution reveal gate')

for marker in [
    "if(state.stage!==1)return true;",
    "if(!stage1ReasoningResolved(s))return '';",
    "const allowFullSolution=state.stage!==1||(state.attempted||[]).includes(1);"
]:
    if marker not in s:
        raise SystemExit(f'missing guardrail {marker}')

p.write_text(s,encoding='utf-8')
print('Stage 1 guardrails applied')
