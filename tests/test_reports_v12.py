import sys,subprocess,time,os,json
from playwright.sync_api import sync_playwright
PORT=int(sys.argv[1]) if len(sys.argv)>1 else 8206
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
srv=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'-d',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
ok=True
def chk(n,c):
    global ok;print(('PASS ' if c else 'FAIL ')+n);ok=ok and bool(c)
BUILD="""async(o)=>{var s=ifxReports._state();Object.assign(s,o.s||{});if(o.mods)s.mods=o.mods;var m=await ifxReports._build();return m.tables.map(function(t){return {sheet:t.sheet,title:t.title,head:t.head,rows:t.rows,total:t.total}})}"""
def tab(ts,sheet): return [t for t in ts if t['sheet']==sheet]
def rowof(t,name,col=0): return [r for r in t['rows'] if r[col]==name]
try:
 with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context(viewport={'width':1100,'height':900},accept_downloads=True);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
  pg.clock.install(time='2026-03-15T09:00:00Z')
  pg.goto(f'http://127.0.0.1:{PORT}/tests/ledger_harness.html');pg.wait_for_timeout(500)
  pg.evaluate("ifxReports.open('bill')");pg.wait_for_timeout(1200)
  txt=pg.inner_text('#ifx-rep').lower()
  chk('UI: 4 steps + report types',all(x in txt for x in ['1 · duration','2 · modules','3 · users','4 · report type','balances only','full breakdown','weekly','monthly','all time','custom dates']))
  chk('UI: old Layout/Include sections are gone','layout' not in txt and 'include' not in txt)
  # ALL TIME, balances, user Alice
  ts=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'},'mods':{'squad':True,'bill':True,'plan':True,'et':False,'bp':False}})
  tp=tab(ts,'Total to pay')[0]; print(json.dumps(tp['rows'])); print(tp['total'])
  bob=rowof(tp,'Bob',0); cara=rowof(tp,'Cara',0); dan=rowof(tp,'Dan',0); own=rowof(tp,'Own plans (card / bank)',0)
  # cols: Pay to, Squad, Bill, EPP, Own, TOTAL, Upcoming
  chk('Bob: squad 270 + plan 100 = 370, upcoming 100',bob and bob[0][1:]==[370,270,0,100,0,100])
  chk('Cara: squad 30 + party 30 + plan -40 = 20',cara and cara[0][1:6]==[20,30,30,-40,0])
  chk('Dan (admin): bill 60',dan and dan[0][1:6]==[60,0,60,0,0])
  chk('Own plans line 50',own and own[0][1]==50 and own[0][5]==50)
  chk('TOTAL TO PAY = 500',tp['total'] and tp['total'][1]==500)
  ow=tab(ts,'Owed to you')[0]; chk('Owed to you empty for Alice',len(ow['rows'])==0)
  sm=tab(ts,'Summary')[0]; allr=[r for r in sm['rows'] if r[0]=='▶ ALL MODULES'][0]; print(allr)
  chk('Summary ALL MODULES pay = 500 (= Total to pay)',allr[1]==500 and allr[2]==0)
  # monthly trail for Feb: Bob squad open 300, charges 250, paid 280, close 270
  h=tab(ts,'Balance history')[0]
  feb=[r for r in h['rows'] if r[0]=='Feb 2026' and r[1]=='Bob' and r[2]=='Squad Split']; print(feb)
  chk('USER EXAMPLE: Feb Squad/Bob open 300 + 250 - 280 = 270',feb and feb[0][4:]==[300,250,280,270] and feb[0][3]=='Pay')
  mar=[r for r in h['rows'] if r[0].startswith('Mar 2026') and r[1]=='Bob' and r[2]=='Squad Split']; chk('Mar Squad/Bob opens 270 (carried forward) closes 270',mar and mar[0][4]==270 and mar[0][7]==270)
  planfeb=[r for r in h['rows'] if r[0]=='Feb 2026' and r[1]=='Bob' and r[2]=='EPP & Gold plans']; chk('Plan/Bob Feb: open 0, +100, close 100',planfeb and planfeb[0][4:]==[0,100,0,100])
  # paid so far
  pd=tab(ts,'Paid so far')[0]; print(json.dumps(pd['rows']))
  bobp=[r for r in pd['rows'] if r[0]=='Bob' and r[1]=='Squad Split']; chk('Paid so far: Bob squad 280 last 2026-02-20',bobp and bobp[0][3]==280 and bobp[0][5]=='2026-02-20')
  dp=[r for r in pd['rows'] if r[0]=='Dan']; chk('Paid so far: Dan 40 on 2026-03-05',dp and dp[0][4]==40 and dp[0][5]=='2026-03-05')
  # FULL breakdown
  tf=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'full'},'mods':{'squad':True,'bill':True,'plan':True,'et':False,'bp':False}})
  sq=tab(tf,'Squad details')[0]; print(len(sq['rows']),'squad detail rows'); chk('Full: squad detail has settlement and carried-forward lines',any('Settlement' in r[2] for r in sq['rows']) and any('carried forward' in r[2] for r in sq['rows']))
  bobrows=[r for r in sq['rows'] if r[1]=='Bob']; chk('Full: running balance ends at 270 for Bob',bobrows and bobrows[-1][5]==270)
  chk('Full: admin, party, plan, own detail tables',all(tab(tf,x) for x in ['Admin details','Party details','Plan details','Own plan details']))
  chk('Full: spending list + squad expenses',tab(tf,'Bill spending list') and tab(tf,'Squad expenses'))
  pdt=tab(tf,'Plan details')[0]; chk('Full: upcoming instalment flagged',any('(upcoming)' in r[2] for r in pdt['rows']))
  # MONTH = Feb, balances
  tm=pg.evaluate(BUILD,{'s':{'dur':'month','month':'2026-02','mode':'bal'}})
  tp2=tab(tm,'Total to pay')[0]; bob2=rowof(tp2,'Bob',0); print(tp2['rows'])
  chk('Feb 2026 closing: Bob squad 270 + plan 100 = 370, upcoming 0 in Feb',bob2 and bob2[0][1]==370 and bob2[0][2]==270 and bob2[0][4]==100 and bob2[0][6]==0)
  # WEEK 9-15 Mar
  tw=pg.evaluate(BUILD,{'s':{'dur':'week','wkDate':'2026-03-12','mode':'bal'}})
  pw=tab(tw,'Total to pay')[0]; chk('Weekly period builds (Mon 9 Mar → Sun 15 Mar)',len(pw['rows'])>=1 and '2026-03-09' in json.dumps(pg.evaluate("ifxReports._periodOf(ifxReports._state())")))
  # BOB perspective: receives
  pg.goto(f'http://127.0.0.1:{PORT}/tests/ledger_harness.html?as=b@x.com');pg.wait_for_timeout(400);pg.evaluate("ifxReports.open('bill')");pg.wait_for_timeout(1000)
  tb=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'},'mods':{'squad':True,'bill':True,'plan':True,'et':False,'bp':False}})
  ob=tab(tb,'Owed to you')[0]; al=rowof(ob,'Alice',0); print(ob['rows'])
  chk("Bob's view: Alice owes him 370 (squad 270 + plan 100)",al and al[0][1]==370 and al[0][2]==270 and al[0][4]==100)
  # ADMIN picks all users
  pg.goto(f'http://127.0.0.1:{PORT}/tests/ledger_harness.html?as=d@x.com');pg.wait_for_timeout(400);pg.evaluate("ifxReports.open('all')");pg.wait_for_timeout(1000)
  txt=pg.inner_text('#ifx-rep'); chk('Admin sees user picker',"All users (4)" in txt)
  ta=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal','scope':'all'},'mods':{'squad':True,'bill':True,'plan':True,'et':True,'bp':True}})
  oa=tab(ta,'Owed to you')[0]; print(oa['head']); chk("Admin 'owed to you': Alice's 60 appears with a User column",oa['head'][0]=='User' and any(r[0]=='Dan' and r[1]=='Alice' and r[2]==60 for r in oa['rows']))
  # downloads
  pg.evaluate("ifxReports._state().scope='all'")
  for kind,sig in (('pdf',b'%PDF'),('xlsx',b'PK'),('csv',b'iFiNeX')):
    with pg.expect_download(timeout=30000) as d: pg.click(f'#ifx-rep [data-a={kind}]')
    chk(f'download {kind}',sig in open(d.value.path(),'rb').read()[:400] or sig in open(d.value.path(),'rb').read())
  # ---- every module has its own entry point ----
  pg.goto(f'http://127.0.0.1:{PORT}/tests/ledger_harness.html');pg.wait_for_timeout(400)
  def entry(name,kind=None):
      pg.evaluate("(a)=>ifxReports.open(a[0],a[1])",[name,{'kind':kind} if kind else None]);pg.wait_for_timeout(900)
      return pg.evaluate("ifxReports._state()")
  for nm in ['bill','squad','plan','card','et','bp']:
      st=entry(nm); on=[k for k,v in st['mods'].items() if v]; chk(f'entry {nm}: only that module is ticked',on==[nm])
  st=entry('all'); chk('entry all: every module ticked',all(st['mods'].values()) and len(st['mods'])==6)
  st=entry('et','trip'); chk('entry trip: tracker type limited to trip',st['kind']=='trip' and 'Trip trackers' in pg.inner_text('#ifx-rep'))
  lst=pg.inner_text('#ifx-rep'); chk('trip entry lists only the trip tracker','Goa trip' in lst and 'Wedding' not in lst)
  tt=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'}}); tr=tab(tt,'Trackers')[0]; chk('trip report contains only the trip tracker',len(tr['rows'])==1 and tr['rows'][0][0]=='Goa trip')
  pg.click('#ifx-rep [data-a=clearkind]');pg.wait_for_timeout(300); chk('clear tracker type -> all types',pg.evaluate("ifxReports._state().kind")=='')
  entry('card'); tc=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'}}); cp=tab(tc,'Card payments')[0]; print(cp['rows'])
  chk('card module: Tabby shared with Bob, 2 dues, 550 due, 250 paid, 300 unpaid',cp['rows'] and cp['rows'][0][:7]==['Tabby','Bob',2,550,250,300,300])
  tcf=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'full'}}); chk('card full: payment lines',len(tab(tcf,'Card payment lines')[0]['rows'])==2)
  entry('plan'); tpl=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'}}); t2=tab(tpl,'Total to pay')[0]; chk('plan-only report: Bob 100 + own plans 50, no squad/bill sheets',rowof(t2,'Bob',0)[0][1]==100 and not tab(tpl,'Bill spending') and not tab(tpl,'Squad summary'))
  entry('squad'); tsq=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'}}); t3=tab(tsq,'Total to pay')[0]; bb=rowof(t3,'Bob',0)[0]; chk('squad-only report: Bob 270, Cara 30',bb[1]==270 and rowof(t3,'Cara',0)[0][1]==30)
  entry('bill'); tbl_=pg.evaluate(BUILD,{'s':{'dur':'all','mode':'bal'}}); t4=tab(tbl_,'Total to pay')[0]; chk('bill-only report: Dan 60 + Cara 30, no Bob',rowof(t4,'Dan',0)[0][1]==60 and rowof(t4,'Cara',0)[0][1]==30 and not rowof(t4,'Bob',0))
  chk('no page errors',not errs); print(errs[:5])
  b.close()
finally:
 srv.terminate()
print('ALL PASS' if ok else 'SOME FAILED');sys.exit(0 if ok else 1)
