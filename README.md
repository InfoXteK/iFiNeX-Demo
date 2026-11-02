# iFiNeX — shared expenses, bills, cards, trackers & budgets (open source)

One codebase, two ways to run:

| Mode | What it is | Needs a server? |
|---|---|---|
| **Standalone** | Everything is stored in your own browser / phone. Single user. | No |
| **Server** | Many users, e-mail-code login, live sync between website and phone app, shared Squad Split. | Yes — a Supabase backend you own |

Website = `web/` (plain HTML/JS, host anywhere static, e.g. GitHub Pages). Android/iOS = `mobile/` (Capacitor wrapper around the same website). Database = `supabase/schema.sql`.

**No real data, keys or URLs are in this repository.** You bring your own backend.

## Live demo
<p align="center"><img src="docs/img/demo-landing.png" width="80%" alt="Demo landing page: choose Website or Mobile app"></p>

After you publish the demo (see `docs/10-LIVE-DEMO.md`, 5 minutes) your repository gets a **Live demo** link at `https://<your-user>.github.io/<repo>/`. It is a full explainer page, not just a preview:

- **Choose Website or Mobile app** on the first screen (or both side by side).
- **17 guided walkthroughs** — each opens the right screen for the right person (admin, member, delegate) and tells you what to try.
- **Request Inspector** — shows every database call the app makes (table, filter, payload) and why the database allows it.
- **Searchable guide to every option and function** (77 entries), a **database explorer** (34 tables + server functions), key flows, roles table and honest limits.
- Includes a clearly labelled **simulated Google Drive** connect / schedule / back-up / restore flow.

Everything uses fictional people and fake data in the browser — no backend.

<p align="center"><img src="docs/img/demo-web.png" width="45%" alt="Website walkthrough"> <img src="docs/img/demo-inspector.png" width="45%" alt="Request inspector"></p>
<p align="center"><img src="docs/img/demo-mobile.png" width="30%" alt="Mobile app demo"> <img src="docs/img/demo-guide.png" width="60%" alt="Searchable feature guide"></p>

Run it locally: `bash demo/build-demo.sh` then `python3 -m http.server -d demo/dist 8181` and open http://localhost:8181 .

## Pick your path
| I want… | Read |
|---|---|
| Quickest: hosted Supabase (free tier) | `docs/01-SUPABASE-CLOUD.md` |
| Everything on my own server (Docker) | `docs/02-SUPABASE-SELF-HOSTED-DOCKER.md` |
| Plain PostgreSQL I already run | `docs/03-PLAIN-POSTGRES.md` |
| MySQL / MariaDB / SQL Server | `docs/04-MYSQL-MSSQL.md` (read this — it is an honest "not directly") |
| Single user, no server | `docs/05-STANDALONE-MODE.md` |
| Publish the website | `docs/06-GITHUB-PAGES.md` |
| Build the Android app | `docs/07-ANDROID.md` |
| Lock it down before real users | `docs/08-SECURITY-CHECKLIST.md` · `docs/09-TRAFFIC-AND-LIMITS.md` |
| Put a live demo link on my repo page | `docs/10-LIVE-DEMO.md` |

## Layout
```
web/       website (+ ifinex-config.example.json)
mobile/    Capacitor Android + iOS projects (mobile/www is a copy of web/, refresh with tools/sync-www.sh)
supabase/  schema.sql (tables, RLS, functions)  ·  hardening.sql (already included in schema.sql; for upgrading old installs)
demo/      live demo (chooser: website / mobile / both)
docs/      guides      .github/workflows/  deploy-web · deploy-demo · android-build
```
License: MIT (see LICENSE). Security: see SECURITY.md.

## What's new in v9.8
Mark as completed / Reopen / Edit / Delete (⋯ menu) and an Active · Completed · All area in the Expense Tracker, EPP & Gold plans and Budget planner; month / custom date / category filters; automatic move to Completed (nightly `ifx_auto_complete()`); faster saving; Android app 2.12.0 no longer requests install/battery permissions (no install-permission warning). Database: run `supabase/schema.sql` on a new project (already includes v9.8).
