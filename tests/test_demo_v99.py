import sys, subprocess, time, os
from playwright.sync_api import sync_playwright
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8187
root = os.path.join(os.path.dirname(__file__), '..', 'demo', 'dist')
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', root], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1); ok = True
def chk(n, c):
    global ok; print(('PASS ' if c else 'FAIL ') + n); ok = ok and bool(c)
B = f'http://127.0.0.1:{PORT}/'
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1500, 'height': 900}); ctx.route(lambda u: 'googleapis.com' in u or 'gstatic.com' in u, lambda r: r.abort()); pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        # landing
        pg.goto(B); pg.wait_for_timeout(800)
        chk('landing: chooser Website', pg.locator('a.opt[href="play.html?device=web"]').count() == 1)
        chk('landing: chooser Mobile', pg.locator('a.opt[href="play.html?device=mobile"]').count() == 1)
        n = pg.locator('details.f').count(); chk(f'landing: catalogue rendered ({n})', n >= 70)
        pg.fill('#q', 'backup'); pg.wait_for_timeout(200); m = pg.locator('details.f').count(); chk(f'landing: search filters ({m})', 0 < m < n)
        pg.fill('#q', ''); pg.fill('#dq', 'gdrive'); pg.wait_for_timeout(200); chk('landing: db filter', pg.locator('#dbt tr').count() == 4)
        chk('landing: 18 scenario cards', pg.locator('#scgrid a').count() == 18)
        # chooser → player (web / mobile)
        pg.click('a.opt[href="play.html?device=web"]'); pg.wait_for_timeout(4000)
        chk('web: Alex frame', pg.frame(name='ifx-demo:alex@demo.test') is not None and 'Alex' in pg.frame(name='ifx-demo:alex@demo.test').inner_text('body'))
        pg.goto(B + 'play.html?device=mobile'); pg.wait_for_timeout(4000)
        chk('mobile: phone frame + Priya', pg.locator('.phone iframe').count() == 1 and pg.frame(name='ifx-demo:priya@demo.test') is not None)
        # all scenarios: every step loads w/o page errors
        ids = pg.evaluate("IFX_SCENARIOS.map(s=>[s.id,s.steps.length])") if False else None
        pg.goto(B + 'play.html'); ids = pg.evaluate("IFX_SCENARIOS.map(s=>[s.id,s.steps.length])")
        for sid, ns in ids:
            pg.goto(B + f'play.html?scenario={sid}'); pg.wait_for_timeout(3500)
            for k in range(ns - 1):
                pg.click('#nxt'); pg.wait_for_timeout(1800)
            chk(f'scenario {sid}: {ns} steps walked', True)
        chk('no page errors during walkthroughs', not errs)
        if errs: print(errs[:5])
        # action + inspector + realtime
        pg.goto(B + 'play.html?scenario=admin&step=2'); pg.wait_for_timeout(4500)
        pg.click('#act'); pg.wait_for_timeout(1200)
        d = pg.evaluate("window.__IFX_DEMO.db.bill_deleted_history.length"); chk('delete-with-reason archived', d == 1)
        chk('priya notified', pg.evaluate("window.__IFX_DEMO.db.bill_notifications.some(n=>n.recipient_email==='priya@demo.test'&&/Duplicate/.test(n.message))"))
        pg.click('.tabs button[data-t=insp]'); chk('inspector shows rpc', 'delete_owed_entry' in pg.inner_text('#calls'))
        # multisquad refusal
        pg.goto(B + 'play.html?scenario=multisquad&step=1'); pg.wait_for_timeout(4000); pg.click('#act'); pg.wait_for_timeout(800)
        chk('member_has_data refusal', pg.evaluate("window.__IFX_DEMO.db.squad_members.filter(r=>r.squad_id===1).length")==4)
        # drive flow
        pg.goto(B + 'play.html?scenario=drive'); pg.wait_for_timeout(4500)
        fr = pg.frame(name='ifx-demo:alex@demo.test')
        fr.get_by_text('Choose Google account & connect').click(); pg.wait_for_timeout(1500)
        chk('drive: simulated google page', 'NOT Google' in pg.frame(name='ifx-demo:alex@demo.test').inner_text('body'))
        pg.frame(name='ifx-demo:alex@demo.test').click('#ok'); pg.wait_for_timeout(6000)
        fr = pg.frame(name='ifx-demo:alex@demo.test')
        chk('drive: connected after return', pg.evaluate("Object.keys(window.__IFX_DEMO.gd.links).length")==1)
        bt = fr.get_by_text('Back up to Google Drive now')
        chk('drive: back-up button', bt.count() > 0)
        if bt.count():
            bt.first.click(); pg.wait_for_timeout(2000)
            chk('drive: backup file created', pg.evaluate("window.__IFX_DEMO.gd.files.length")==1)
        # standalone mobile width
        pg.set_viewport_size({'width': 390, 'height': 800}); pg.goto(B); pg.wait_for_timeout(600)
        chk('landing fits phone width', pg.evaluate("document.documentElement.scrollWidth<=392"))
        pg.screenshot(path=os.path.join(root, '..', 'shot-landing-mobile.png'))
        # both.html still works
        pg.set_viewport_size({'width': 1500, 'height': 900}); pg.goto(B + 'both.html'); pg.wait_for_timeout(3500); pg.click('#s3'); pg.wait_for_timeout(1200)
        chk('both.html realtime', 'DELETE bill_owed' in pg.inner_text('#feed'))
        chk('no page errors overall', not errs)
        if errs: print(errs[:5])
        b.close()
finally:
    srv.terminate()
sys.exit(0 if ok else 1)
