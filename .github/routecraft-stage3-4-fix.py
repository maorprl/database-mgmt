from pathlib import Path
import re, subprocess

BASE='f58511c605244b30b0a4b9a479261fa260dc0215'
p=Path('sql-lab/index.html')
s=p.read_text(encoding='utf-8')
base=subprocess.check_output(['git','show',f'{BASE}:sql-lab/index.html'],text=True)
if s != base:
    raise SystemExit('branch app is not byte-for-byte current main before patch')

def replace_once(text, old, new, label):
    n=text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {n}')
    return text.replace(old,new,1)

# Stage 3: generic reasoning language; keep the named seed instance only for post-run verification.
s=replace_once(
    s,
    'ב-Riverbend Crossdock יש 3 drivers ו-3 routes. אם נחבר את שני ענפי ה-M גולמית, כמה rows ייווצרו עבורה?',
    'אם ל-depot יש 3 drivers ו-3 routes, כמה rows ייווצרו בחיבור גולמי של שני ענפי ה-M?',
    'stage3 fanout question')
s=replace_once(
    s,
    'Riverbend יצרה 9 rows בחיבור הגולמי, אבל ה-Output Grain הוא depot. כמה פעמים Riverbend צריכה להופיע בתוצאה הסופית?',
    'בחיבור הגולמי depot עם 3 drivers ו-3 routes יצרה 9 rows, אבל ה-Output Grain הוא depot. כמה פעמים אותה depot צריכה להופיע בתוצאה הסופית?',
    'stage3 pre-SQL sanity wording')

# Stage 4: remove learner-facing course-design labels.
s=replace_once(s,'eye:"Transfer · אותו M→1 על relation חדשה"','eye:"מסלול → רכב · קשר M→1"','stage4 eyebrow')
s=replace_once(
    s,
    'pred:"זהו Transfer: אין כאן operator חדש. מפעילים על routes ו-vehicles את אותה דרך חשיבה שכבר נלמדה."',
    'pred:"התחילו מה-Grain, ואז השתמשו ב-keys וב-constraints כדי להבין את הקשר בין routes ל-vehicles."',
    'stage4 prediction intro')
s=replace_once(
    s,
    'q:"לפי ה-constraints שמוצגים מעל, לכמה vehicles יכולה route אחת להתאים דרך vehicle_id?"',
    'q:"לכמה vehicles יכולה route אחת להתאים דרך vehicle_id?"',
    'stage4 q2 wording')
s=replace_once(
    s,
    'principle:"Transfer: כש-FK NOT NULL של ה-child מפנה ל-PK של parent, לכל child יש match יחיד; צירוף attributes מה-parent שומר על Grain של ה-child."',
    'principle:"כש-FK NOT NULL של ה-child מפנה ל-PK של parent, לכל child יש match יחיד; צירוף attributes מה-parent שומר על Grain של ה-child."',
    'stage4 principle')
s=replace_once(
    s,
    "const stageTitle=state.stage===4?'Transfer · מפעילים את אותה דרך חשיבה':((state.stage===1||state.stage===2||guidedCourseStage())?'מפרקים את הבקשה העסקית':'המודל הרלציוני');",
    "const stageTitle=(state.stage===1||state.stage===2||state.stage===4||guidedCourseStage())?'מפרקים את הבקשה העסקית':'המודל הרלציוני';",
    'stage4 relational title')

# Stage 4: question first, then the exact information needed, then options.
start=s.index('function stage4PredictionQuizHtml(s){')
end=s.index('function stage4TransferNoteHtml(){', start)
new='''function stage4PredictionQuizHtml(s){
 const byStage=(state.predAnswers||{})[4]||{};
 const renderQ=(qi,afterQuestion='')=>{
   const q=s.predQuiz[qi],cur=byStage[qi]||'',checked=predQuestionChecked(4,qi),correct=checked&&cur===q.ans;
   const concept=(correct&&q.concept)?'<div class="stage1-concept-close"><b>קבענו:</b> '+esc(q.concept)+'</div>':'';
   const msg=(checked&&cur)?('<div class="answer-exp '+(correct?'good':'wrong')+'"><b>'+(correct?'נכון. ':'עוד לא. ')+'</b>'+esc(correct?q.why:(q.wrong||'חזרו למידע שמופיע בשאלה.'))+concept+'</div>'):'';
   return '<div class="pred-q"><label>'+(qi+1)+'. '+esc(q.q)+'</label>'+afterQuestion+'<select data-predq="'+qi+'"><option value="">בחרו...</option>'+q.opts.map(o=>'<option value="'+esc(o[0])+'" '+(cur===o[0]?'selected':'')+'>'+esc(o[1])+'</option>').join('')+'</select><div class="actions"><button class="check" data-check-pred="'+qi+'">✓ בדוק תשובה</button></div>'+msg+'</div>';
 };
 let out=renderQ(0);
 if(predQuestionResolved(4,s,0))out+=renderQ(1,stage4RelationsHtml());
 if(predQuestionResolved(4,s,1))out+=renderQ(2,'<div class="stage1-concept-note"><p>לכל route יש match אחד בדיוק ב-vehicles.</p></div>');
 return '<div class="pred-quiz">'+out+'</div>';
}
'''
s=s[:start]+new+s[end:]

old_note='''function stage4TransferNoteHtml(){
 return '<div class="stage1-concept-note"><h4>Transfer — אין כאן operator חדש</h4><p>זה אותו pattern מפרק 1: מתחילים מצד ה-M, עוברים דרך Foreign Key ל-row יחידה בצד ה-1, ומוסיפים attributes בלי לשנות את ה-Grain.</p></div>';
}'''
new_note='''function stage4TransferNoteHtml(){
 return '<div class="stage1-concept-note"><h4>אותו קשר, relation חדשה</h4><p>כבר ראינו את הדפוס הזה: מתחילים מצד ה-M, עוברים דרך Foreign Key ל-row יחידה בצד ה-1, ומוסיפים attributes בלי לשנות את ה-Grain.</p></div>';
}'''
s=replace_once(s,old_note,new_note,'stage4 transfer note')

for x in [
    'Transfer · מפעילים את אותה דרך חשיבה',
    'eye:"Transfer · אותו M→1 על relation חדשה"',
    'pred:"זהו Transfer:',
    'ב-Riverbend Crossdock יש 3 drivers ו-3 routes.',
    'Riverbend יצרה 9 rows בחיבור הגולמי'
]:
    if x in s:
        raise SystemExit(f'forbidden learner-facing text remains: {x}')

for x in [
    'eye:"מסלול → רכב · קשר M→1"',
    'אם ל-depot יש 3 drivers ו-3 routes, כמה rows ייווצרו בחיבור גולמי של שני ענפי ה-M?',
    'renderQ(1,stage4RelationsHtml())',
    'לכל route יש match אחד בדיוק ב-vehicles.',
    "return '<div class=\"pred-q\"><label>'+(qi+1)+'. '+esc(q.q)+'</label>'+afterQuestion+'<select",
    'state.stage===1||state.stage===2||state.stage===4||guidedCourseStage()',
    '<h4>אותו קשר, relation חדשה</h4>'
]:
    if x not in s:
        raise SystemExit(f'required contract marker missing: {x}')

# Verify only Stage 3 and Stage 4 objects changed inside STAGES.
def stage_spans(text):
    marker='const STAGES='
    a=text.index(marker)+len(marker)
    if text[a] != '[':
        raise SystemExit('STAGES array start changed')
    depth=0; quote=None; esc=False; end=None
    for i in range(a,len(text)):
        c=text[i]
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
            continue
        if c in ('"',"'",'`'): quote=c; continue
        if c=='[': depth+=1
        elif c==']':
            depth-=1
            if depth==0: end=i; break
    if end is None:
        raise SystemExit('STAGES end not found')
    spans=[]; depth=0; quote=None; esc=False; st=a+1
    for i in range(a+1,end):
        c=text[i]
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        else:
            if c in ('"',"'",'`'): quote=c
            elif c in '{[(': depth+=1
            elif c in '}])': depth-=1
            elif c==',' and depth==0:
                l=st
                while l<i and text[l].isspace(): l+=1
                r=i
                while r>l and text[r-1].isspace(): r-=1
                spans.append((l,r)); st=i+1
    l=st
    while l<end and text[l].isspace(): l+=1
    r=end
    while r>l and text[r-1].isspace(): r-=1
    if l<r: spans.append((l,r))
    return spans

bspan=stage_spans(base); nspan=stage_spans(s)
if len(bspan)!=24 or len(nspan)!=24:
    raise SystemExit(f'unexpected stage count base={len(bspan)} new={len(nspan)}')
bobj=[base[l:r] for l,r in bspan]; nobj=[s[l:r] for l,r in nspan]
changed=[i for i,(a,b) in enumerate(zip(bobj,nobj)) if a!=b]
if changed != [3,4]:
    raise SystemExit(f'unexpected changed STAGES: {changed}')

p.write_text(s,encoding='utf-8')

# JavaScript syntax.
scripts=[]
for attrs,body in re.findall(r'<script([^>]*)>(.*?)</script>',s,re.S|re.I):
    if 'src=' not in attrs.lower():
        scripts.append(body)
Path('/tmp/routecraft-inline.js').write_text('\n'.join(scripts),encoding='utf-8')
subprocess.run(['node','--check','/tmp/routecraft-inline.js'],check=True)
