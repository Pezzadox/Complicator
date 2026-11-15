import sys
from playwright.sync_api import sync_playwright
import os
path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html')
path=os.path.abspath(path)
def ok(c,m): print(('PASS ' if c else 'FAIL ')+m)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True)
    pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file://'+path); pg.wait_for_timeout(600)
    def tap(k): pg.click(f'#keys button[aria-label="{k}"]')
    def typenum(n):
        for ch in str(abs(n)): tap(ch)
        if n<0: tap('minus')
    bad=pg.evaluate("""()=>{let bad=0;for(let n of [2,4,8])for(let t=-50;t<=500;t++)for(let k=0;k<10;k++){const s=generate(t,n);let v=s[0].a;for(const x of s){if(x.a!==v)bad++;v=calc(x.a,x.op,x.b);if(v!==x.res||!Number.isInteger(v))bad++}if(v!==t||s.length!==n)bad++}return bad}""")
    ok(bad==0,'generator: 16,530 chains all valid')
    ok(pg.evaluate("()=>{for(let i=0;i<2000;i++){const v=evaluate(surpriseSum());if(v===null||!Number.isInteger(v)||v<0)return false}return true}"),'surprise sums always whole and >=0')
    ok(pg.evaluate("()=>[evaluate('2+3×4'),evaluate('−5'),evaluate('8÷2÷2')]")==[14,None,2],'evaluate precedence/guards')
    # backspace in input
    for k in ['1','2','delete','plus','1','equals']: tap(k)
    ok(pg.evaluate("()=>L().expr")=='1+1' and pg.evaluate("()=>L().phase")=='solve','backspace while typing sum')
    # wrong answers -> hint -> reveal
    s=pg.evaluate("()=>L().steps[0]")
    for i in range(3):
        typenum(s['res']+1); tap('equals')
    l=pg.evaluate("()=>L()")
    ok(l['hint'] and l['revealed'] and 'It' in l['note'],'2 misses -> hint, 3 -> gentle reveal: '+l['note'])
    pg.screenshot(path='/tmp/v2_reveal.png')
    # backspace in entry
    tap('9'); tap('9'); tap('delete'); ok(pg.evaluate("()=>L().entry")=='9','backspace while answering')
    tap('delete')
    # solve all
    steps=pg.evaluate("()=>L().steps")
    for st in steps[pg.evaluate("()=>L().idx"):]:
        typenum(st['res']); tap('equals')
    ok(pg.evaluate("()=>L().phase")=='done','puzzle A solved'); ok(pg.evaluate("()=>S.stats.streak")==0,'streak not counted after reveal (honest)')
    pg.wait_for_timeout(300); pg.screenshot(path='/tmp/v2_done.png')
    # lanes: start B via surprise, partial, jump to C, back to B keeps progress
    pg.click('#lanes button:nth-child(2)'); pg.click('#aSurprise')
    st=pg.evaluate("()=>L().steps[0]"); typenum(st['res']); tap('equals')
    pg.click('#lanes button:nth-child(3)'); ok(pg.evaluate("()=>L().phase")=='input','lane C fresh')
    pg.click('#lanes button:nth-child(2)'); ok(pg.evaluate("()=>L().idx")==1,'lane B kept its progress after jumping away')
    ok(pg.inner_text('#lanes button:nth-child(1) i')=='solved','lane A shows solved')
    pg.screenshot(path='/tmp/v2_lanes.png')
    # new route keeps target
    t=pg.evaluate("()=>L().target"); pg.click('#aRoute'); ok(pg.evaluate("()=>L().target")==t and pg.evaluate("()=>L().idx")==0,'new route: same answer, restarts')
    # clean solve -> streak
    for st in pg.evaluate("()=>L().steps"): typenum(st['res']); tap('equals')
    ok(pg.evaluate("()=>S.stats.streak")==1,'clean solve adds to streak')
    # flow mode auto next
    pg.evaluate("()=>{S.set.flow=true}"); pg.click('#aSurprise')
    for st in pg.evaluate("()=>L().steps"): typenum(st['res']); tap('equals')
    pg.wait_for_timeout(1900); ok(pg.evaluate("()=>L().phase")=='solve','flow mode loads next puzzle by itself')
    # persistence
    pg.reload(); pg.wait_for_timeout(400); ok(pg.evaluate("()=>S.lane")==1 and pg.evaluate("()=>S.stats.streak")>=1,'progress survives reload')
    # settings sheet
    pg.click('#openSettings'); pg.wait_for_timeout(200); pg.screenshot(path='/tmp/v2_settings.png')
    pg.click('[data-set=calm]'); pg.click('[data-set=easy]'); pg.click('#closeSettings')
    ok(pg.evaluate("()=>document.body.classList.contains('calm')&&document.body.classList.contains('easy')"),'calm + easy-read toggles apply')
    pg.screenshot(path='/tmp/v2_calm.png')
    pg.click('#aFocus'); pg.wait_for_timeout(100); pg.screenshot(path='/tmp/v2_focus.png')
    pg.click('#aFocus')
    # break nudge
    pg.evaluate("()=>{S.focusMs=S.set.breakMin*60000+1000}"); pg.wait_for_timeout(1200)
    ok(pg.evaluate("()=>document.getElementById('breakVeil').classList.contains('open')"),'break nudge appears after set time')
    pg.click('#brMain'); pg.wait_for_timeout(1100); pg.screenshot(path='/tmp/v2_break.png'); pg.click('#brMain')
    ok(not pg.evaluate("()=>document.getElementById('breakVeil').classList.contains('open')"),'break closes and puzzles still there')
    # 8D + layouts
    pg.evaluate("()=>{localStorage.clear()}"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("()=>{S.set.level=2}"); pg.click('#aSurprise')
    for vp in [(320,568),(360,640),(375,667),(390,844),(430,932)]:
        pg.set_viewport_size({'width':vp[0],'height':vp[1]}); pg.wait_for_timeout(150)
        r=pg.evaluate("""()=>{const kb=document.querySelector('.keys').getBoundingClientRect().bottom;const st=document.querySelector('.stack').getBoundingClientRect();const top=document.querySelector('.lanes').getBoundingClientRect().bottom;
          const over=[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&!b.closest('.veil')).some(b=>b.scrollWidth>b.clientWidth+1);
          return {fits:document.documentElement.scrollHeight<=innerHeight+1&&kb<=innerHeight, stackClear:(getComputedStyle(document.querySelector('.stack')).display==='none')||st.top>=top-1, textOverflow:over}}""")
        ok(r['fits'] and r['stackClear'] and not r['textOverflow'],f'8D layout {vp}: {r}')
        pg.screenshot(path=f'/tmp/v2_8d_{vp[0]}x{vp[1]}.png')
    ok(not errs,'no JS errors '+str(errs))
    b.close()
