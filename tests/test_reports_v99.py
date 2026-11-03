import sys,subprocess,time,os,base64
from playwright.sync_api import sync_playwright
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8194
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','demo','dist')
srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'-d',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
ok=True
def chk(n,c):
    global ok;print(('PASS ' if c else 'FAIL ')+n);ok=ok and bool(c)
def dl(pg,f,sel):
    with pg.expect_download(timeout=15000) as d: f.click(sel)
    path=d.value.path(); return d.value.suggested_filename, open(path,'rb').read()
try:
 with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context(viewport={'width':1200,'height':900},accept_downloads=True);c.route(lambda u:'googleapis.com' in u or 'gstatic.com' in u,lambda r:r.abort());pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.on('console',lambda m: print('CONSOLE',m.text[:200]) if m.type=='error' else None)
  pg.on('dialog',lambda d:d.accept())
  # ---------- Bill Tracker (admin Alex)
  pg.goto(f'http://127.0.0.1:{PORT}/play.html?scenario=spend&user=alex');pg.wait_for_timeout(5500)
  f=pg.frame(name='ifx-demo:alex@demo.test')
  f.evaluate("switchPage('home')");pg.wait_for_timeout(500)
  f.click('#btn-email-report');pg.wait_for_timeout(1500)
  chk('report center opens (bill)', f.locator('#ifx-rep.open').count()==1)
  txt=f.inner_text('#ifx-rep'); chk('has period+users+layout', all(x in txt for x in ['This month','Custom dates','All users','One section per user','Monthly summary']))
  f.click('#ifx-rep [data-k=preset][data-v=all]');f.click('#ifx-rep [data-k=scope][data-v=all]');pg.wait_for_timeout(300)
  f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2500)
  pv=f.inner_text('#rp-prev'); print(pv[:400].replace('\n',' | '))
  chk('preview has summary + multiple users', 'Summary' in pv and 'Alex' in pv and 'Priya' in pv)
  n,data=dl(pg,f,'#ifx-rep [data-a=pdf]'); chk('PDF downloaded', n.endswith('.pdf') and data[:4]==b'%PDF')
  n,data=dl(pg,f,'#ifx-rep [data-a=xlsx]'); chk('Excel downloaded', n.endswith('.xlsx') and data[:2]==b'PK')
  n,data=dl(pg,f,'#ifx-rep [data-a=csv]'); chk('CSV downloaded', n.endswith('.csv') and b'Bill Tracker report' in data)
  # chosen users + custom dates + monthly
  f.click('#ifx-rep [data-k=scope][data-v=pick]');f.click('#ifx-rep [data-a=nou]');pg.wait_for_timeout(200)
  f.locator('#ifx-rep input[data-u]').nth(1).check()
  f.click('#ifx-rep [data-k=preset][data-v=custom]');f.fill('#ifx-rep input[data-f=from]','2000-01-01');f.fill('#ifx-rep input[data-f=to]','2999-01-01')
  f.click('#ifx-rep [data-k=group][data-v=month]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2500)
  pv2=f.inner_text('#rp-prev'); chk('custom: one chosen user, monthly table', 'Spending per month' in pv2 and pv2.count('Alex')<=3)
  f.fill('#ifx-rep input[data-f=from]','2999-01-01');f.fill('#ifx-rep input[data-f=to]','2000-01-01');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(800)
  chk('bad date range refused', 'swap' in f.inner_text('#rp-msg'))
  # old report overlay exports use safe saver
  f.evaluate("ifxReports.close()")
  # ---------- native app simulation
  f.evaluate("""window.__calls=[];window.Capacitor={isNativePlatform:()=>true,Plugins:{Filesystem:{writeFile:async o=>{window.__calls.push(['write',o.path,o.directory,o.data.length]);return{uri:'file:///cache/'+o.path}}},Share:{share:async o=>{window.__calls.push(['share',o.url]);return{}}}}}""")
  f.evaluate("ifxReports.open('bill')");pg.wait_for_timeout(1500)
  f.click('#ifx-rep [data-a=pdf]');pg.wait_for_timeout(3000)
  calls=f.evaluate("window.__calls"); print(calls)
  chk('native path: writeFile(CACHE) then Share', len(calls)==2 and calls[0][0]=='write' and calls[0][2]=='CACHE' and calls[0][3]>1000 and calls[1][0]=='share')
  f.evaluate("window.Capacitor={isNativePlatform:()=>true,Plugins:{}}");f.evaluate("ifxReports.close();ifxReports.open('bill')");pg.wait_for_timeout(1200)
  f.click('#ifx-rep [data-a=xlsx]');pg.wait_for_timeout(2500)
  chk('native without plugins: visible fallback box (no silent failure)', f.locator('a[download$=".xlsx"]').count()==1)
  f.evaluate("delete window.Capacitor;ifxReports.close()")
  # ---------- Squad Split
  pg.goto(f'http://127.0.0.1:{PORT}/play.html?scenario=squad&user=alex');pg.wait_for_timeout(5500)
  f=pg.frame(name='ifx-demo:alex@demo.test')
  btn=f.locator('#btn-email-squad-report'); chk('squad button is Reports', 'Reports' in btn.inner_text())
  f.evaluate("ifxReports.open('squad')");pg.wait_for_timeout(1500)
  chk('squad center opens with members', f.locator('#ifx-rep input[data-u]').count()>=3)
  f.click('#ifx-rep [data-k=preset][data-v=all]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2500)
  pv=f.inner_text('#rp-prev'); print(pv[:500].replace('\n',' | '))
  chk('squad preview: members summary + expenses', 'Members' in pv and 'Fuel' in pv or 'Cabin' in pv)
  f.click('#ifx-rep [data-a=nou]');f.locator('#ifx-rep input[data-u]').nth(0).check();f.click('#ifx-rep [data-k=group][data-v=combined]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2000)
  chk('squad: chosen member only (summary rows=1)', f.locator('#rp-prev table.rp-t').first.locator('tr').count()<=3)
  n,data=dl(pg,f,'#ifx-rep [data-a=pdf]'); chk('squad PDF', data[:4]==b'%PDF')
  n,data=dl(pg,f,'#ifx-rep [data-a=xlsx]'); chk('squad Excel', data[:2]==b'PK')
  chk('no page errors', not errs); print(errs[:3])
  b.close()
finally:
 srv.terminate()
print('ALL PASS' if ok else 'SOME FAILED')
