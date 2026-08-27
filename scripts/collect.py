#!/usr/bin/env python3
"""绿透工作台 · 本地数据采集
扫 git 仓库 + Obsidian vault 的待办，生成 workbench-data.js（放在 workbench.html 旁边）。
只用标准库，不联网，不写任何仓库或 vault 文件。

用法:
  python3 collect.py --projects ~/projects --vault ~/path/to/vault --out ~/Downloads
"""
import argparse, json, os, re, subprocess, sys, time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

def sh(args, cwd=None):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""

def scan_git(root: Path, limit=14):
    repos = []
    if not root.is_dir():
        return repos
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")) or not (d / ".git").exists():
            continue
        ct = sh(["git", "-C", str(d), "log", "-1", "--format=%ct"])
        if not ct.isdigit():
            continue
        branch = sh(["git", "-C", str(d), "branch", "--show-current"]) or "detached"
        dirty = len([l for l in sh(["git", "-C", str(d), "status", "--porcelain"]).splitlines() if l.strip()])
        subject = sh(["git", "-C", str(d), "log", "-1", "--format=%s"])[:40]
        today = sh(["git", "-C", str(d), "log", "--since=midnight", "--oneline"])
        remote = sh(["git", "-C", str(d), "remote", "get-url", "origin"])
        if remote.startswith("git@"):
            remote = "https://" + remote[4:].replace(":", "/", 1)
        remote = re.sub(r"\.git$", "", remote) if remote.startswith("https://") else ""
        month0 = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        days = sh(["git", "-C", str(d), "log", "--since", month0, "--date=short", "--format=%ad"])
        repos.append({
            "name": d.name, "branch": branch, "dirty": dirty,
            "last": int(ct), "subject": subject, "path": str(d), "remote": remote,
            "commitsToday": len(today.splitlines()) if today else 0,
            "days": days.splitlines() if days else [],
        })
    repos.sort(key=lambda r: r["last"], reverse=True)
    return repos[:limit]

TASK_RE = re.compile(r"^\s*[-*] \[( |x|X)\] +(.+)$")

def scan_vault(vault: Path, max_tasks=6, max_backlog=5, max_files=500):
    todos, backlog, done_today = [], [], 0
    if not vault or not vault.is_dir():
        return todos, backlog, done_today
    now = time.time()
    today0 = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
    md = []
    skip = {".obsidian", ".git", ".trash", "55_附件", "50_资源", "00_收件箱", "存档", "归档"}
    for p in vault.rglob("*.md"):
        if any(part in skip or part.startswith(".") for part in p.parts[len(vault.parts):]):
            continue
        try:
            mt = p.stat().st_mtime
        except OSError:
            continue
        md.append((mt, p))
    md.sort(reverse=True)
    seen = set()
    for mt, p in md[:max_files]:
        if len(todos) >= max_tasks and len(backlog) >= max_backlog:
            break
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            m = TASK_RE.match(line)
            if not m:
                continue
            mark, body = m.group(1), m.group(2).strip()
            body = re.sub(r"[#*`\[\]]", "", body).strip()[:24]
            # 过滤链接、纯符号、过短占位（"待添加"这类无信息条目）
            if (not body or body in seen or len(body) < 4
                    or body.startswith(("http://", "https://", "www."))):
                continue
            seen.add(body)
            if mark != " ":
                if mt >= today0:
                    done_today += 1
                continue
            age = int((now - mt) / 86400)
            src = p.stem[:12]
            relf = str(p.relative_to(vault))
            if age >= 7 and len(backlog) < max_backlog:
                backlog.append({"text": body, "days": age, "src": src, "file": relf})
            elif age < 7 and len(todos) < max_tasks:
                todos.append({"text": body, "badge": "待办", "tone": "todo",
                              "time": datetime.fromtimestamp(mt).strftime("%m-%d"), "src": src, "file": relf})
    return todos, backlog, done_today

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects", required=True)
    ap.add_argument("--vault", default="")
    ap.add_argument("--todo-file", default="", help="指定一个 md，其中未勾选项直接进今日队列")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()

    repos = scan_git(Path(a.projects).expanduser())
    todos, backlog, done_today = scan_vault(Path(a.vault).expanduser() if a.vault else None)
    if a.todo_file:
        tf = Path(a.todo_file).expanduser()
        if tf.is_file():
            curated = []
            for line in tf.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = TASK_RE.match(line)
                if m and m.group(1) == " ":
                    body = re.sub(r"[#*`\[\]]", "", m.group(2)).strip()[:24]
                    if body:
                        curated.append({"text": body, "badge": "待办", "tone": "todo",
                                        "time": "", "src": tf.stem[:12]})
            if curated:
                todos = curated[:8]

    running = [r for r in repos if r["dirty"] > 0]
    stale = [r for r in repos if time.time() - r["last"] > 14 * 86400]
    commits_today = sum(r["commitsToday"] for r in repos)

    def status(r):
        if r["dirty"] > 0: return "在跑"
        if time.time() - r["last"] > 14 * 86400: return "久置"
        return "干净"

    def rel(ts):
        d = int((time.time() - ts) / 86400)
        return "今天" if d == 0 else ("昨天" if d == 1 else f"{d} 天前")

    projects = [{
        "name": r["name"], "branch": r["branch"], "dirty": r["dirty"],
        "when": rel(r["last"]), "note": r["subject"], "status": status(r),
        "path": r["path"], "remote": r["remote"],
    } for r in repos]

    ring = [{"id": f"RP · {i+1:02d}", "name": r["name"], "branch": r["branch"],
             "dirty": r["dirty"], "status": status(r), "note": r["subject"], "when": rel(r["last"]),
             "path": r["path"], "remote": r["remote"]}
            for i, r in enumerate(repos[:5])]

    top = repos[0] if repos else None
    daily = Counter()
    for r in repos:
        daily.update(r["days"])
    refresh_cmd = "python3 " + os.path.abspath(__file__) + " --projects " + a.projects + \
        (" --vault " + a.vault if a.vault else "") + \
        (" --todo-file " + a.todo_file if a.todo_file else "") + " --out " + a.out
    data = {
        "generated": datetime.now().strftime("%m-%d %H:%M"),
        "generatedEpoch": int(time.time()),
        "vaultName": Path(a.vault).expanduser().resolve().name if a.vault else "",
        "dailyCommits": dict(daily),
        "refreshCmd": refresh_cmd,
        "stats": [
            {"cap": "Today / 今日提交", "name": "跨仓库提交", "value": str(commits_today), "unit": "个",
             "note": "已完成待办", "delta": f"✓ {done_today}", "tone": "up"},
            {"cap": "Running / 在跑", "name": "有未提交改动", "value": str(len(running)), "unit": "个仓库",
             "note": "共", "delta": f"{sum(r['dirty'] for r in running)} 处改动", "tone": "up"},
            {"cap": "Pending / 待办", "name": "近 7 天待办", "value": str(len(todos)), "unit": "项",
             "note": "来自", "delta": "vault 勾选框", "tone": "warn"},
            {"cap": "Backlog / 久置", "name": "超两周未动", "value": str(len(stale)), "unit": "个仓库",
             "note": "最久", "delta": rel(stale[-1]["last"]) if stale else "无", "tone": "risk"},
        ],
        "queue": {"today": todos, "backlog": backlog},
        "projects": projects,
        "ring": ring,
        "ringFocus": 0,
        "detail": top and {
            "code": f"REPO · {top['name'].upper()[:12]}",
            "name": top["name"], "badge": "最近活跃",
            "desc": f"最近提交：{top['subject']}",
            "rows": [["当前分支", f"{top['branch']}" + (f" · +{top['dirty']}" if top["dirty"] else "")],
                     ["最近提交", rel(top["last"])],
                     ["当前状态", ("●" if top["dirty"] else "") + status(top)]],
            "advice": ([f"{r['name']} 有 {r['dirty']} 处未提交改动" for r in running[:2]] +
                       [f"{r['name']} 已 {rel(r['last'])}未动" for r in stale[:1]])[:3] or ["一切干净，无待处理事项"],
        },
    }

    out = Path(a.out).expanduser() / "workbench-data.js"
    out.write_text("window.WORKBENCH_LIVE = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
                   encoding="utf-8")
    print(f"ok: {out}  ({len(repos)} repos, {len(todos)} todos, {len(backlog)} backlog)")

if __name__ == "__main__":
    main()
