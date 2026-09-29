import json, os, re, datetime as dt, requests

CFG = json.load(open("config.json"))
TODAY = dt.date.today().isoformat()
UA = {"User-Agent": "job-tracker/1.0"}

def get(url, **kw):
    try:
        r = requests.get(url, headers=UA, timeout=30, **kw); r.raise_for_status(); return r.json()
    except Exception as e:
        print("skip", url.split("?")[0], e); return {}

def strip(h): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h or "")).strip()

def job(title, company, loc, region, url, date, text):
    return dict(title=title, company=company, location=loc, region=region, url=url, date=(date or "")[:10], text=strip(text))

def adzuna():
    if not os.environ.get("ADZUNA_ID"): print("no Adzuna keys"); return []
    out = []
    for cc, extra in CFG["countries"].items():
        for q in CFG["queries"]:
            d = get(f"https://api.adzuna.com/v1/api/jobs/{cc}/search/1", params=dict(
                app_id=os.environ["ADZUNA_ID"], app_key=os.environ["ADZUNA_KEY"], results_per_page=50,
                what=f"{q} {extra}".strip(), max_days_old=CFG["max_days_old"], sort_by="date"))
            for j in d.get("results", []):
                out.append(job(j["title"], j["company"]["display_name"], j["location"]["display_name"],
                    {"in": "India", "us": "US remote", "gb": "UK remote"}[cc], j["redirect_url"], j["created"], j["description"]))
    return out

def remotive():
    d = get("https://remotive.com/api/remote-jobs", params={"search": "data engineer"})
    return [job(j["title"], j["company_name"], j["candidate_required_location"], "Remote", j["url"],
                j["publication_date"], j["description"]) for j in d.get("jobs", [])]

def boards():
    out = []
    for t in CFG["greenhouse"]:
        for j in get(f"https://boards-api.greenhouse.io/v1/boards/{t}/jobs?content=true").get("jobs", []):
            out.append(job(j["title"], t, j["location"]["name"], "Company board", j["absolute_url"], j["updated_at"], j.get("content", "")))
    for c in CFG["lever"]:
        d = get(f"https://api.lever.co/v0/postings/{c}?mode=json")
        for j in (d if isinstance(d, list) else []):
            out.append(job(j["text"], c, j["categories"].get("location", ""), "Company board", j["hostedUrl"],
                           dt.datetime.fromtimestamp(j["createdAt"] / 1000).isoformat(), j.get("descriptionPlain", "")))
    return out

def years(t):
    m = [int(x) for x in re.findall(r"(\d{1,2})\s*(?:\+|-\s*\d{1,2})?\s*(?:years|yrs)", t.lower())]
    return min(m) if m else None

def main():
    prev = {}
    if os.path.exists("docs/jobs.json"):
        prev = {j["url"]: j for j in json.load(open("docs/jobs.json"))["jobs"]}
    seen, res = set(), []
    for j in adzuna() + remotive() + boards():
        if j["url"] in seen or not any(t in j["title"].lower() for t in CFG["title_terms"]): continue
        seen.add(j["url"])
        blob = f'{j["title"]} {j["company"]} {j["text"]}'.lower()
        y = years(j["text"])
        if y and y > CFG["max_years"]: continue
        j["years"] = y
        j["skills"] = [s for s in CFG["skills"] if re.search(rf"\b{re.escape(s)}\b", blob)]
        j["pharma"] = any(p in blob for p in CFG["pharma_terms"])
        j["score"] = len(j["skills"]) * 10 + (25 if j["pharma"] else 0) - (abs(y - 2) * 3 if y else 0)
        j["first_seen"] = prev.get(j["url"], {}).get("first_seen", TODAY)
        j["text"] = j["text"][:300]
        res.append(j)
    res.sort(key=lambda j: -j["score"])
    data = {"updated": TODAY, "jobs": res}
    json.dump(data, open("docs/jobs.json", "w"))
    page = open("template.html").read().replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    open("docs/index.html", "w").write(page)
    print(len(res), "jobs")

main()
