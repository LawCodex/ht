#!/usr/bin/env python3
"""Fetch Haitian legislation available from official sites and convert it
to Markdown.

Sources
  * Direction Générale du Budget (Ministère de l'Économie et des Finances),
    "Cadre réglementaire": https://budget.gouv.ht/cadre-reglementaire/<cat>
    for cat in Constitution, Lois, Décrets, Arrêtés, Comptes Spéciaux.
  * Parlement haïtien, archived by the Internet Archive (the site
    parlementhaitien.ht is offline): text of the 1987 Constitution,
    http://www.parlementhaitien.ht/telechargements/constitution.pdf
    (capture 2011-06-17).
PDFs are cached in _raw/ht/pdf/. Scans without a text layer are skipped.
Usage: ht_fetch.py
"""
import datetime
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

import requests
from bs4 import BeautifulSoup

UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "ht"))
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TODAY = datetime.date.today().isoformat()
BUDGET = "https://budget.gouv.ht/cadre-reglementaire/"
CATS = {"Constitution": "constitution", "Lois": "lois", "D%C3%A9crets": "decrets",
        "Arre%CC%82te%CC%81s": "arretes", "Comptes%20Sp%C3%A9ciaux": "comptes-speciaux"}
ARCHIVED = [{
    "title": "Constitution de la République d'Haïti (29 mars 1987)",
    "url": "https://web.archive.org/web/20110617022113id_/http://www.parlementhaitien.ht:80/telechargements/constitution.pdf",
    "original": "http://www.parlementhaitien.ht/telechargements/constitution.pdf",
    "date_text": "29 mars 1987", "cat": "constitution", "file": "parl-constitution.pdf"}]
MONTHS = {m: i + 1 for i, m in enumerate(["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout",
                                          "septembre", "octobre", "novembre", "decembre"])}
s = requests.Session()
s.headers["User-Agent"] = UA


def get(url):
    for i in range(5):
        try:
            r = s.get(url, timeout=300)
            time.sleep(2)
            if r.status_code in (200, 404, 403):
                return r
        except requests.RequestException as e:
            print("retry", url, e, file=sys.stderr)
        time.sleep(5 * (i + 1))
    raise RuntimeError(url)


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    return head == b"%PDF-" and b"%%EOF" in tail and \
        subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def deacc(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def slug(t, n=90):
    return re.sub(r"[^a-z0-9]+", "-", deacc(t).lower()).strip("-")[:n].rstrip("-")


def parse_date(t):
    t = unicodedata.normalize("NFC", t)
    m = re.search(r"(\d{1,2})(?:er)?\s+(\w+)\.?\s+(\d{4})", t)
    if not m:
        return ""
    mo = MONTHS.get(deacc(m.group(2)).lower())
    return "%s-%02d-%02d" % (m.group(3), mo, int(m.group(1))) if mo else ""


def index():
    ip = os.path.join(RAW, "index.json")
    if os.path.exists(ip):
        return json.load(open(ip))
    items = []
    for c, d in CATS.items():
        soup = BeautifulSoup(get(BUDGET + c).text, "lxml")
        for tr in soup.find_all("tr"):
            a = tr.find("a", href=re.compile(r"\.pdf$"))
            btn = tr.find("button", attrs={"data-target": True})
            if not a or not btn:
                continue
            modal = soup.find(id=btn["data-target"].lstrip("#"))
            title = modal.find(class_="modal-title").get_text(" ", strip=True) if modal else btn.get_text(" ", strip=True)
            tds = tr.find_all("td")
            items.append({"title": htmlmod.unescape(title), "url": a["href"], "cat": d, "category_page": BUDGET + c,
                          "date_text": tds[1].get_text(" ", strip=True) if len(tds) > 1 else "",
                          "file": a["href"].rsplit("/", 1)[1]})
    items += ARCHIVED
    json.dump(items, open(ip, "w"), indent=1, ensure_ascii=False)
    return items


HEAD_RE = re.compile(r"^(TITRE|CHAPITRE|SECTION|TITLE|CHAPTER)\s+([IVXLC]+|\d+|[A-Z]|PREMIER|UNIQUE)\b.{0,100}$", re.I)
ART_RE = re.compile(r"^(Article|ARTICLE|Art\.)\s+(\d+(?:[.-]\d+)*(?:\s*(?:bis|ter|er))?|premier|PREMIER|unique|UNIQUE)\s*[.:\-–]*\s*(.*)$")


def to_md(path):
    txt = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True).stdout.decode("utf-8", "replace")
    pages = txt.split("\f")
    if len(re.sub(r"\s", "", txt)) < 150 * max(1, len(pages) - 1):
        return None
    out = []
    for p in pages:
        for line in p.split("\n"):
            st = re.sub(r"\s+", " ", line).strip()
            if not st:
                if out and out[-1] != "":
                    out.append("")
                continue
            if re.fullmatch(r"[-– ]*\d{1,3}[-– ]*", st):
                continue
            if HEAD_RE.match(st) and st.upper() == st:
                out += ["", "## " + st, ""]
                continue
            m = ART_RE.match(st)
            if m:
                out += ["", "### Article " + m.group(2), ""]
                if m.group(3):
                    out.append(m.group(3))
                continue
            if re.match(r"^[#>*+\-=|`]", st):
                st = "\\" + st
            st = re.sub(r"^(\d+)([.)])(\s)", r"\1\\\2\3", st)
            out.append(st)
        if out and out[-1] != "":
            out.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def yq(t):
    return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    items = index()
    gaps, counts, used = [], {}, set()
    for it in items:
        if it["cat"] == "constitution" and it["title"] == "Constitution du 29 Mars 1987":
            continue  # same 1987 text as the (more complete) Parliament copy below
        p = os.path.join(RAW, "pdf", it["file"])
        if not pdf_ok(p):
            r = get(it["url"])
            if r.status_code == 200 and r.content[:5] == b"%PDF-":
                open(p, "wb").write(r.content)
        if not pdf_ok(p):
            gaps.append((it["title"], it["url"], "download failed"))
            continue
        body = to_md(p)
        if body is None:
            gaps.append((it["title"], it["url"], "scanned PDF without text layer"))
            continue
        date = parse_date(it["title"]) or parse_date(it.get("date_text", ""))
        cat = it["cat"]
        typ = {"constitution": "constitution", "lois": "loi", "decrets": "decret", "arretes": "arrete"}.get(cat, "")
        if cat == "comptes-speciaux":
            typ = "loi" if it["title"].lower().startswith("loi") else "decret"
            cat = "lois" if typ == "loi" else "decrets"
        status = "in_force"
        sub = cat
        if cat == "constitution":
            t = it["title"].lower()
            if "1957" in t or "1964" in t:
                status, sub = "repealed", "constitution/historique"
            elif "loi constitutionnelle" in t:
                typ = "loi constitutionnelle"
        fn = (date[:4] + "-" if date and sub != "constitution" else "") + slug(it["title"]) + ".md"
        path = os.path.join(OUT, sub, fn)
        if path in used:
            path = path[:-3] + "-2.md"
        used.add(path)
        fm = ["---", "title: " + yq(it["title"]), "type: " + yq(typ), "jurisdiction: ht", "language: fr"]
        if date:
            fm.append("date: " + date)
        if it.get("date_text") and it["date_text"] != it["title"]:
            fm.append("published: " + yq(it["date_text"]))
        fm += ["status: " + status, "source: " + yq(it.get("original") or it["url"])]
        if it.get("original"):
            fm.append("archived_copy: " + yq(it["url"]))
        if typ == "constitution" and status == "in_force":
            fm.append('note: "Original 1987 text. Not consolidated: the Loi constitutionnelle of 9 May 2011 '
                      '(published 19 June 2012) amending it is not included (scanned PDF only)."')
        fm += ["retrieved: " + TODAY, "---"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write("\n".join(fm) + "\n\n# " + it["title"] + "\n\n" + body)
        counts[sub] = counts.get(sub, 0) + 1
    json.dump(gaps, open(os.path.join(RAW, "gaps.json"), "w"), indent=1, ensure_ascii=False)
    print(counts)
    for g in gaps:
        print("GAP", g)


if __name__ == "__main__":
    main()
