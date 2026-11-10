# -*- coding: utf-8 -*-
"""
README 자동 갱신 스크립트

하는 일
1. til/ 폴더의 메모(TIL)를 날짜순으로 모아서
   - README.md 의 <!-- TIL:START --> ~ <!-- TIL:END --> 사이에 최근 5개를 넣고
   - til/README.md 에 전체 목록(주제별)을 만든다
2. 1mo.dev 레포(옆에 체크아웃된 폴더)의 git 기록을 보고
   최근에 새로 쓰거나 고친 문서 5개를 <!-- 1MO:START --> ~ <!-- 1MO:END --> 사이에 넣는다

외부 라이브러리 없이 파이썬 기본 기능만 쓴다.
"""
import os
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIL_DIR = os.path.join(ROOT, "til")
README = os.path.join(ROOT, "README.md")
# 1mo-tech-interview 레포를 체크아웃해 둔 위치 (워크플로에서 지정)
ONEMO_DIR = os.environ.get("ONEMO_DIR", os.path.join(ROOT, "_1mo"))
SITE = "https://1mo.dev"
# 프로필 화면에서도 링크가 깨지지 않도록 절대 주소를 쓴다
REPO_URL = "https://github.com/dubu-alt/dubu-alt/blob/main"
TREE_URL = "https://github.com/dubu-alt/dubu-alt/tree/main"
LIMIT = 5


def read_frontmatter(path):
    """맨 위 --- 사이의 title, date, draft 값을 읽는다."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    meta = {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def collect_tils():
    """til/주제/파일.md 를 모두 읽어서 (날짜, 주제, 제목, 경로) 목록으로 만든다."""
    items = []
    for dirpath, _, files in os.walk(TIL_DIR):
        for name in files:
            if not name.endswith(".md") or name.startswith("_") or name == "README.md":
                continue
            path = os.path.join(dirpath, name)
            meta = read_frontmatter(path)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            topic = os.path.relpath(dirpath, TIL_DIR).replace(os.sep, "/")
            items.append({
                "date": meta.get("date", "0000-00-00"),
                "topic": "기타" if topic == "." else topic,
                "title": meta.get("title", name[:-3]),
                "rel": rel,
            })
    items.sort(key=lambda x: (x["date"], x["title"]), reverse=True)
    return items


def recent_1mo_docs():
    """1mo.dev 레포의 git 기록에서 최근에 바뀐 글을 중복 없이 뽑는다."""
    if not os.path.isdir(os.path.join(ONEMO_DIR, ".git")):
        print("1mo 레포가 없어서 1mo.dev 목록은 건너뜀", file=sys.stderr)
        return None
    log = subprocess.run(
        ["git", "-c", "core.quotepath=false", "log", "--format=@@%ad", "--date=short",
         "--name-only", "--diff-filter=AM", "--", "docs"],
        cwd=ONEMO_DIR, capture_output=True, text=True, check=True,
    ).stdout
    seen, docs, date = set(), [], ""
    for line in log.splitlines():
        line = line.strip()
        if line.startswith("@@"):
            date = line[2:]
            continue
        if not line.endswith(".md") or line in seen:
            continue
        seen.add(line)
        full = os.path.join(ONEMO_DIR, line)
        if not os.path.exists(full) or line.endswith("index.md"):
            continue  # 지워진 글, 첫 화면은 제외
        meta = read_frontmatter(full)
        if meta.get("draft") == "true":
            continue  # 공개 안 한 글은 제외
        path = line[len("docs/"):-len(".md")]
        docs.append({
            "date": date,
            "title": meta.get("title", os.path.basename(path)),
            "url": SITE + "/" + quote(path),
        })
        if len(docs) >= LIMIT:
            break
    return docs


def replace_block(text, tag, body):
    pattern = re.compile(r"(<!-- %s:START -->).*?(<!-- %s:END -->)" % (tag, tag), re.S)
    return pattern.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), text)


def main():
    with open(README, encoding="utf-8") as f:
        readme = f.read()

    tils = collect_tils()
    til_lines = ["- `%s` [%s](%s/%s)" % (t["date"], t["title"], REPO_URL, quote(t["rel"])) for t in tils[:LIMIT]]
    til_lines.append("")
    til_lines.append("전체 %d개 보기 → [til/](%s/til)" % (len(tils), TREE_URL))
    readme = replace_block(readme, "TIL", "\n".join(til_lines))

    docs = recent_1mo_docs()
    if docs is not None:
        doc_lines = ["- `%s` [%s](%s)" % (d["date"], d["title"], d["url"]) for d in docs]
        doc_lines.append("")
        doc_lines.append("더 보기 → [1mo.dev](%s)" % SITE)
        readme = replace_block(readme, "1MO", "\n".join(doc_lines))

    with open(README, "w", encoding="utf-8") as f:
        f.write(readme)

    # til/README.md : 주제별 전체 목록
    out = ["# TIL (Today I Learned)", "", "공부하다 새로 알게 된 것을 짧게 적어 두는 곳이에요. 총 %d개." % len(tils), ""]
    for topic in sorted({t["topic"] for t in tils}):
        out.append("## %s" % topic)
        out.append("")
        for t in [x for x in tils if x["topic"] == topic]:
            out.append("- `%s` [%s](%s)" % (t["date"], t["title"], t["rel"][len("til/"):]))
        out.append("")
    with open(os.path.join(TIL_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("TIL %d개, 1mo 문서 %s개 반영" % (len(tils), "건너뜀" if docs is None else len(docs)))


if __name__ == "__main__":
    main()
