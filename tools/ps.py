#!/usr/bin/env python3
"""Problem Solving toolkit (no extra packages needed).

  python tools/ps.py new <url>     create the solution file from a problem link and open it in VS Code
  python tools/ps.py listen        receive Competitive Companion clicks from the browser (port 10045)
  python tools/ps.py sync [files]  push each solution's footer to Notion (run by the git hook after a commit)

Add --dry-run to `sync` to print what would be sent without calling Notion.
"""
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("PS_PORT", "10045"))
# My Problems database. If you fork this, set NOTION_DATABASE_ID / NOTION_DATA_SOURCE_ID in .env.
DEFAULT_DB = "41cea90596468167ba58f98204bb5e56"
DEFAULT_DS = "41cea905-9646-81f1-82c1-000bbd95cd04"
REVIEW_GAPS = [1, 3, 7, 21]                               # days until next review, after review 0,1,2,3
SOLVE_DIRS = ("codeforces", "leetcode", "atcoder", "cses", "other")

WENT = {"easy": "Solo easy", "struggled": "Solo struggled", "hint": "Needed hint", "editorial": "Needed editorial"}
SOURCE_ALIASES = [  # (substring in what you typed, Notion option)
    ("saad", "Mostafa Saad Sheet"), ("icpc", "ICPC L1"), ("lc daily", "LC Daily"), ("daily", "LC Daily"),
    ("lc contest", "LC Contest"), ("cf contest", "CF Contest"), ("contest", "CF Contest"), ("lc", "LC Other"),
]
TAG_ALIASES = {
    "dfs and similar": "dfs/bfs", "depth-first search": "dfs/bfs", "breadth-first search": "dfs/bfs",
    "constructive algorithms": "constructive", "dynamic programming": "dp", "hash table": "hashing",
    "prefix sum": "prefix sums", "stack": "stack/queue", "queue": "stack/queue", "tree": "trees",
    "binary tree": "trees", "graph": "graphs", "string": "strings", "sorting": "sortings",
    "bit manipulation": "bitmasks",
}

FOOTER = """

// ------------------------------------------------------------
// {id} — {title}
// {url}
// Sources: {sources}
// Went:    (easy | struggled | hint | editorial)
// Insight:
"""


# ---------------------------------------------------------------- helpers

def log(msg):
    print(msg, flush=True)
    try:
        with open(ROOT / "tools" / "listener.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}\n")
    except OSError:
        pass


def http_json(url, body=None, headers=None, method=None, timeout=10):
    h = {"User-Agent": "problem-solving-toolkit", "Content-Type": "application/json"}
    h.update(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=h, method=method or ("POST" if data else "GET"))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def identify(raw):
    """Problem link -> {id, path, platform, url, ...}. LeetCode needs leetcode_fill() afterwards."""
    url = raw.strip()
    if "vjudge.net/contest" in url:
        raise ValueError("That's a VJudge contest link. Open the problem's 'Origin' page and use that link.")
    url = url.split("?")[0].split("#")[0].rstrip("/")

    m = re.search(r"vjudge\.net/problem/([A-Za-z]+)-(.+)$", url)
    if m:
        oj, pid = m.group(1).lower(), m.group(2)
        if oj == "codeforces" and re.match(r"\d+[A-Za-z]\d?$", pid):
            c, p = re.match(r"(\d+)(\w+)$", pid).groups()
            url = f"https://codeforces.com/problemset/problem/{c}/{p}"
        elif oj == "atcoder":
            url = f"https://atcoder.jp/contests/{pid.rsplit('_', 1)[0]}/tasks/{pid}"
        elif oj == "cses":
            url = f"https://cses.fi/problemset/task/{pid}"
        else:
            return {"id": f"{oj.upper()}-{pid}", "path": f"other/{oj}-{pid}.cpp", "platform": "Other", "url": url}

    m = (re.search(r"codeforces\.(?:com|net)/(?:contest|gym)/(\d+)/problem/(\w+)", url)
         or re.search(r"codeforces\.(?:com|net)/problemset/problem/(\d+)/(\w+)", url))
    if m:
        c, p = m.group(1), m.group(2).upper()
        return {"id": f"CF-{c}{p}", "path": f"codeforces/{c}{p}.cpp", "platform": "Codeforces",
                "url": url, "contest": c, "index": p}
    m = re.search(r"leetcode\.com/problems/([^/]+)", url)
    if m:
        return {"id": None, "slug": m.group(1), "platform": "LeetCode",
                "url": f"https://leetcode.com/problems/{m.group(1)}/"}
    m = re.search(r"atcoder\.jp/contests/[^/]+/tasks/([^/]+)", url)
    if m:
        return {"id": f"AC-{m.group(1)}", "path": f"atcoder/{m.group(1)}.cpp", "platform": "AtCoder", "url": url}
    m = re.search(r"cses\.fi/problemset/task/(\d+)", url)
    if m:
        return {"id": f"CSES-{m.group(1)}", "path": f"cses/{m.group(1)}.cpp", "platform": "CSES", "url": url}
    raise ValueError("Unknown judge. Supported: Codeforces, LeetCode, AtCoder, CSES, and VJudge problem links.")


def cf_meta(contest, index):
    if int(contest) >= 100000:  # gym: no ratings
        return {}
    d = http_json(f"https://codeforces.com/api/contest.standings?contestId={contest}&from=1&count=1")
    for p in d["result"]["problems"]:
        if p["index"].upper() == index.upper():
            return {"title": p["name"], "rating": p.get("rating"), "tags": p.get("tags", [])}
    return {}


def lc_meta(slug):
    q = {"query": "query q($s:String!){question(titleSlug:$s){questionFrontendId title difficulty topicTags{name}}}",
         "variables": {"s": slug}}
    d = http_json("https://leetcode.com/graphql", q, {"Referer": "https://leetcode.com"})["data"]["question"]
    return {"number": int(d["questionFrontendId"]), "title": d["title"], "difficulty": d["difficulty"],
            "tags": [t["name"] for t in d["topicTags"]]}


def leetcode_fill(info, ask=True):
    try:
        meta = lc_meta(info["slug"])
        n, info["title"] = meta["number"], meta["title"]
    except Exception:
        if not ask:
            n = None
        else:
            n = int(input("LeetCode problem number: ").strip())
    if n is None:
        info["id"], info["path"] = f"LC-{info['slug']}", f"leetcode/{info['slug']}.cpp"
    else:
        info["id"], info["path"] = f"LC-{n}", f"leetcode/{n:04d}-{info['slug']}.cpp"
    return info


def create(info, title="", tests=None):
    """Create the solution file (template on top, footer at the bottom). Returns (path, existed)."""
    path = ROOT / info["path"]
    existed = path.exists()
    if not existed:
        path.parent.mkdir(parents=True, exist_ok=True)
        tpl = ROOT / "templates" / ("leetcode.cpp" if info["platform"] == "LeetCode" else "template.cpp")
        body = tpl.read_text(encoding="utf-8").rstrip() + "\n"
        path.write_text(body + FOOTER.format(id=info["id"], title=title or info.get("title", ""),
                                             url=info["url"], sources=""), encoding="utf-8", newline="\n")
    inp = path.parent / "input.txt"
    if tests:
        inp.write_text(tests[0].get("input", ""), encoding="utf-8")
        (path.parent / "expected.txt").write_text(tests[0].get("output", ""), encoding="utf-8")
    elif not inp.exists():
        inp.touch()
    return path, existed


def open_in_vscode(*paths):
    try:
        subprocess.Popen(["code", "-r", str(ROOT), *map(str, paths)], shell=(os.name == "nt"))
    except OSError:
        log("VS Code ('code') not found in PATH. Open the file manually.")


def start(raw_url, title="", tests=None, ask=True):
    info = identify(raw_url)
    if info["platform"] == "LeetCode":
        leetcode_fill(info, ask=ask)
    elif info["platform"] == "Codeforces" and not title:
        try:
            title = cf_meta(info["contest"], info["index"]).get("title", "")
        except Exception:
            pass
    path, existed = create(info, title, tests)
    if existed:
        log(f"!! {info['id']} already exists: {info['path']}")
        log("   Check Notion first: easy last time -> skip it; struggled -> 2-min recall, then re-solve from scratch.")
    else:
        log(f"Created {info['path']}")
    open_in_vscode(path, path.parent / "input.txt")
    return info


# ---------------------------------------------------------------- new

def cmd_new(args):
    url = args[0] if args else input("Problem URL: ")
    try:
        start(url)
    except ValueError as e:
        print(e)
        sys.exit(1)


# ---------------------------------------------------------------- listen (Competitive Companion)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode())
            title = re.sub(r"^[A-Z]\d?\.\s*", "", data.get("name", ""))  # "A. Theatre Square" -> "Theatre Square"
            start(data["url"], title=title, tests=data.get("tests"), ask=False)
        except Exception as e:
            log(f"Couldn't create problem: {e}")
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


def cmd_listen(args):
    log(f"Listening for Competitive Companion on port {PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


# ---------------------------------------------------------------- sync (Notion)

def parse_footer(text):
    """Read the footer block. Returns None if there is no ID line."""
    ids = list(re.finditer(r"^\s*//\s*([A-Z]+-[\w-]+)\s+[—–-]\s*(.*)$", text, re.M))
    if not ids:
        return None
    f = {"id": ids[-1].group(1), "title": ids[-1].group(2).strip()}

    def field(name):
        m = list(re.finditer(rf"^\s*//\s*{name}:[ \t]*(.*)$", text, re.M))
        v = m[-1].group(1).strip() if m else ""
        return "" if v.startswith("(") else v

    f["url"] = (re.findall(r"^\s*//\s*(https?://\S+)\s*$", text, re.M) or [""])[-1]
    f["sources"] = [s.strip() for s in re.split(r"[,;]", field("Sources")) if s.strip()]
    f["went"] = field("Went").lower()
    f["has_went"] = bool(re.search(r"^\s*//\s*Went:", text, re.M))
    f["insight"] = field("Insight")
    return f


def map_source(s):
    low = s.lower()
    for key, name in SOURCE_ALIASES:
        if key in low:
            return name
    return s


def map_tag(t):
    t = t.lower()
    return TAG_ALIASES.get(t, t)


def env_get(key, default=None):
    """Read a setting from the environment or from .env."""
    val = os.environ.get(key)
    env = ROOT / ".env"
    if not val and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(key + "="):
                val = line.split("=", 1)[1].strip()
    return val or default


def env_token():
    return env_get("NOTION_TOKEN")


class Notion:
    def __init__(self, token):
        self.token = token
        self.version = "2025-09-03"
        self.db = env_get("NOTION_DATABASE_ID", DEFAULT_DB)
        self.ds = env_get("NOTION_DATA_SOURCE_ID", DEFAULT_DS)

    def call(self, method, path, body=None):
        h = {"Authorization": f"Bearer {self.token}", "Notion-Version": self.version}
        try:
            return http_json(f"https://api.notion.com/v1/{path}", body, h, method)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Notion {e.code}: {e.read().decode()[:300]}") from None

    def find(self, pid):
        flt = {"filter": {"property": "ID", "rich_text": {"equals": pid}}}
        try:
            res = self.call("POST", f"data_sources/{self.ds}/query", flt)
        except RuntimeError:
            self.version = "2022-06-28"  # older API fallback
            res = self.call("POST", f"databases/{self.db}/query", flt)
        return res["results"][0] if res["results"] else None

    def save(self, page, props):
        if page:
            return self.call("PATCH", f"pages/{page['id']}", {"properties": props})
        parent = ({"type": "data_source_id", "data_source_id": self.ds} if self.version >= "2025"
                  else {"database_id": self.db})
        return self.call("POST", "pages", {"parent": parent, "properties": props})


def github_link(rel):
    try:
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip()
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", remote)
        return f"https://github.com/{m.group(1)}/blob/HEAD/{urllib.parse.quote(rel)}" if m else None
    except OSError:
        return None


def build_props(f, rel, page, today):
    old = (page or {}).get("properties", {})
    solved_before = (old.get("Status", {}).get("status") or {}).get("name") in ("Solved", "Upsolved")
    reviews = old.get("Reviews", {}).get("number") or 0

    if not solved_before:          # first solve
        reviews, gap = 0, (None if f["went"] == "easy" else 1)
    else:                          # a re-solve = a review
        reviews += 1
        passed = f["went"] in ("easy", "struggled")
        gap = (REVIEW_GAPS[reviews] if reviews < len(REVIEW_GAPS) else None) if passed else 1

    platform = {"CF": "Codeforces", "LC": "LeetCode", "AC": "AtCoder", "CSES": "CSES"}.get(f["id"].split("-")[0], "Other")
    sources = {o["name"] for o in old.get("Sources", {}).get("multi_select", [])} | {map_source(s) for s in f["sources"]}
    title = f["title"]

    p = {
        "ID": {"rich_text": [{"text": {"content": f["id"]}}]},
        "Platform": {"select": {"name": platform}},
        "Status": {"status": {"name": "Solved"}},
        "How It Went": {"select": {"name": WENT[f["went"]]}},
        "Reviews": {"number": reviews},
        "Next Review": {"date": {"start": str(today + datetime.timedelta(days=gap))} if gap else None},
    }
    if sources:
        p["Sources"] = {"multi_select": [{"name": s} for s in sorted(sources)]}
    if f["url"]:
        p["Link"] = {"url": f["url"]}
    if f["insight"]:
        p["Key Insight"] = {"rich_text": [{"text": {"content": f["insight"][:1900]}}]}
    if not solved_before:
        p["Solved On"] = {"date": {"start": str(today)}}

    # metadata from the judge (only fills what's missing)
    meta = {}
    try:
        if platform == "Codeforces":
            m = re.match(r"CF-(\d+)([A-Z]\d?)$", f["id"])
            meta = cf_meta(*m.groups()) if m else {}
        elif platform == "LeetCode" and f["url"]:
            meta = lc_meta(re.search(r"problems/([^/]+)", f["url"]).group(1))
    except Exception:
        pass
    title = title or meta.get("title") or f["id"]
    p["Problem"] = {"title": [{"text": {"content": title}}]}
    if meta.get("rating") and not old.get("Rating", {}).get("number"):
        p["Rating"] = {"number": meta["rating"]}
    if meta.get("difficulty"):
        p["Difficulty"] = {"select": {"name": meta["difficulty"]}}
    if meta.get("tags") and not old.get("Tags", {}).get("multi_select"):
        p["Tags"] = {"multi_select": [{"name": t} for t in sorted({map_tag(t) for t in meta["tags"]})]}
    link = github_link(rel)
    if link:
        p["Code"] = {"url": link}
    return p


def committed_files():
    msg = subprocess.run(["git", "log", "-1", "--pretty=%B"], cwd=ROOT, capture_output=True, text=True).stdout
    if "[skip notion]" in msg.lower():
        return []
    out = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "HEAD"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def cmd_sync(args):
    dry = "--dry-run" in args
    files = [a for a in args if a != "--dry-run"] or committed_files()
    files = [f.replace("\\", "/") for f in files if f.replace("\\", "/").split("/")[0] in SOLVE_DIRS]
    if not files:
        return
    token = env_token()
    if not token and not dry:
        print("[notion] No NOTION_TOKEN in .env, skipped. Run setup.cmd once.")
        return
    notion = Notion(token) if not dry else None
    today = datetime.date.today()
    for rel in files:
        path = ROOT / rel
        if not path.exists():
            continue
        f = parse_footer(path.read_text(encoding="utf-8", errors="replace"))
        if not f or not f["has_went"]:
            continue
        if f["went"] not in WENT:
            print(f"[notion] {f['id']}: skipped (fill 'Went:' with easy / struggled / hint / editorial)")
            continue
        try:
            page = notion.find(f["id"]) if notion else None
            props = build_props(f, rel, page, today)
            if dry:
                print(json.dumps({rel: props}, ensure_ascii=False, indent=1))
                continue
            notion.save(page, props)
            nr = props["Next Review"]["date"]
            print(f"[notion] {f['id']}: {'updated' if page else 'added'}"
                  + (f", next review {nr['start']}" if nr else ""))
        except Exception as e:
            print(f"[notion] {f['id']}: failed: {e}")


if __name__ == "__main__":
    cmds = {"new": cmd_new, "listen": cmd_listen, "sync": cmd_sync}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]](sys.argv[2:])
