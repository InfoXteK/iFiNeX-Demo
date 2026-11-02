# 10 — Live demo on your repository page

What visitors get: a **Live demo** link in the repository sidebar and README. Click it and choose **Website** or **Mobile app** (or both side by side). Fake people, fake data, runs only in the browser.

A README cannot run an app inside itself (GitHub strips scripts and iframes). The standard way is a link plus screenshots, which is what this does.

## Publish it (5 minutes, no tools)
1. GitHub → your repository → **Settings → Pages → Source: GitHub Actions**.
2. Repository → **Actions** → *Deploy interactive demo (GitHub Pages)* → **Run workflow**. Wait for the green tick.
3. The demo address is shown in that run (usually `https://YOUR-USER.github.io/YOUR-REPO/`). Open it and check.
4. Repository main page → ⚙ next to **About** → tick **Use your GitHub Pages website** (or paste the demo address in *Website*) → Save. The link now shows in the sidebar.
5. Put the address in the README badge/link line at the top.

Only one Pages site per repository: if this repo already serves your real website, copy the built `demo/dist` into a sub-folder (e.g. `demo/`) of that site instead, or create a second repository for the demo.

## Rebuild after changing the web code
`bash demo/build-demo.sh` (or push: the workflow runs by itself on changes in `demo/` or `web/`).

## What it contains (demo v9.8)
- `demo/index.html` — landing / explainer: Website-or-Mobile chooser, how the demo works, modules, roles table, 17 walkthrough cards, searchable guide of every option (`features-a.js`, `features-b.js`), database explorer (`dbdata.js`), flows, run-it-yourself, honest limits.
- `demo/play.html` + `scenarios.js` — the player: device switch (website / phone frame), module + user switch (Alex admin · Priya member · Sam delegate), guided steps with "do it for me" actions, **Request Inspector** (every table call + payload + plain-English reason).
- `demo/demo-backend.js` — replaces the Supabase client with an in-browser stand-in (tables, filters, RPCs, realtime, tiny trigger stand-ins, storage, simulated Google Drive edge function). The real website code runs unchanged.
- `demo/demo-google.html` — clearly labelled simulated Google consent page.
- `demo/both.html` — website + phone side by side with a realtime feed.
- Edit the guide text in `features-a.js` / `features-b.js`; add a walkthrough in `scenarios.js`.
- Tests (need Playwright): `python3 tests/test_demo_v98.py 8187` (landing, chooser, all 17 walkthroughs, inspector, delete-with-reason, Drive flow, phone width) and `python3 tests/test_demo.py 8186`.

## v9.8 additions
`features-c.js` (7 entries: Completed lifecycle, filters, auto-complete, faster saving, update flow without install warning), walkthroughs `lifecycle` and `filters`, DB explorer shows `status / completed_at / auto_complete` and `ifx_auto_complete()`. Test: `python3 tests/test_lifecycle_v98.py` (port 8192).
