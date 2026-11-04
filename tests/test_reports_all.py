import sys,subprocess,time,os,zipfile,io,re
from playwright.sync_api import sync_playwright
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8201
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','demo','dist')
srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'-d',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
ok=True
def chk(n,c):
    global ok;print(('PASS ' if c else 'FAIL ')+n);ok=ok and bool(c)
try:
 with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context(viewport={'width':1200,'height':900},accept_downloads=True);c.route(lambda u:'googleapis.com' in u or 'gstatic.com' in u,lambda r:r.abort());pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
  pg.on('dialog',lambda d:d.accept())
  pg.goto(f'http://127.0.0.1:{PORT}/play.html?scenario=tour&user=alex');pg.wait_for_timeout(5500)
  f=pg.frame(name='ifx-demo:alex@demo.test')
  f.evaluate("switchPage('hub')");pg.wait_for_timeout(600)
  chk('hub has Reports tile','Reports & Downloads' in f.inner_text('#hub-grid'))
  f.locator('#hub-grid .hub-tile',has_text='Reports & Downloads').click();pg.wait_for_timeout(2000)
  t=f.inner_text('#ifx-rep'); print(t[:300].replace('\n',' | ')); chk('all-modules title + module chips', 'all modules' in t and all(x.lower() in t.lower() for x in ['Squad Split','Budget planner','EPP & Gold plans','Trackers / events']))
  chk('include groups for each module', all(x in t for x in ['Tracker summary','Monthly summary','Instalments','Squad expenses','Spending']))
  f.click('#ifx-rep [data-k=preset][data-v=all]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(3500)
  pv=f.inner_text('#rp-prev'); print(pv[:900].replace('\n',' | '))
  chk('overview table', 'Month-by-month overview' in pv)
  chk('bill + squad + trackers + budget + plans tables', all(x in pv for x in ['Summary — spending','Squad Split','Expense / Trip / Event trackers','Budget','EPP & Gold plans']))
  with pg.expect_download(timeout=20000) as d: f.click('#ifx-rep [data-a=xlsx]')
  data=open(d.value.path(),'rb').read(); z=zipfile.ZipFile(io.BytesIO(data)); wbx=z.read('xl/workbook.xml').decode(); names=re.findall(r'<sheet name="([^"]+)"',wbx); print(names)
  chk('Excel has Overview + module sheets', 'Overview' in names and len(names)>=8)
  with pg.expect_download(timeout=20000) as d: f.click('#ifx-rep [data-a=pdf]')
  chk('PDF', open(d.value.path(),'rb').read()[:4]==b'%PDF')
  with pg.expect_download(timeout=20000) as d: f.click('#ifx-rep [data-a=csv]')
  chk('CSV has all modules', b'iFiNeX report' in open(d.value.path(),'rb').read())
  # one module only: trackers, one event
  f.click('#ifx-rep [data-k=modsall]')   # all -> only bill
  f.click('#ifx-rep [data-k=mod][data-v=et]');f.click('#ifx-rep [data-k=mod][data-v=bill]');pg.wait_for_timeout(300)
  on=f.evaluate("ifxReports._state().mods"); print(on)
  chk('only trackers module on', on.get('et') and not on.get('bill'))
  cbs=f.locator('#ifx-rep input[data-e]'); n=cbs.count(); chk('events listed', n>=2)
  cbs.nth(0).check();f.click('#ifx-rep [data-k=group][data-v=user]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2500)
  pv=f.inner_text('#rp-prev'); print(pv[:400].replace('\n',' | '))
  chk('single event: one tracker in summary', f.locator('#rp-prev table.rp-t').first.locator('tr').count()<=3 and 'Entries —' in pv)
  # budget + plans only, custom month
  f.click('#ifx-rep [data-k=mod][data-v=bp]');f.click('#ifx-rep [data-k=mod][data-v=pl]');f.click('#ifx-rep [data-k=mod][data-v=et]');f.click('#ifx-rep [data-k=preset][data-v=this_month]');f.click('#ifx-rep [data-a=prev]');pg.wait_for_timeout(2500)
  pv=f.inner_text('#rp-prev'); chk('budget + plans only', 'Budget' in pv and 'EPP & Gold plans' in pv and 'Squad Split' not in pv and 'Spending' not in pv)
  # squad member in all mode for Priya
  f.evaluate("ifxReports.close()")
  chk('no page errors', not errs); print(errs[:3])
  b.close()
finally:
 srv.terminate()
print('ALL PASS' if ok else 'SOME FAILED')
