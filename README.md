# Job Feed (auto-updating)

Fetches data-engineer jobs daily (India, US remote, UK remote), scores them against your skills, flags pharma/healthcare,
hides roles asking for more than `max_years`, and publishes a web page.

## Setup (10 minutes, free)
1. Get free API keys at https://developer.adzuna.com (App ID + App Key).
2. Create a GitHub repo, upload these files. Repo > Settings > Secrets and variables > Actions: add `ADZUNA_ID` and `ADZUNA_KEY`.
3. Settings > Pages: Source = "Deploy from a branch", Branch = main, folder = /docs.
4. Actions tab > "Fetch jobs" > Run workflow. Your page appears at https://<username>.github.io/<repo>/
5. It then refreshes every day at 08:00 IST.

## Customise
Edit `config.json`: queries, skills, pharma terms, max_years. Add company boards: put Greenhouse/Lever board names in
`greenhouse` / `lever` (the slug in boards.greenhouse.io/<slug> or jobs.lever.co/<slug>).
Saved/Applied/Ignored marks are stored in your browser only.
Run locally: `pip install requests; ADZUNA_ID=... ADZUNA_KEY=... python fetch_jobs.py`, then open docs/index.html.
