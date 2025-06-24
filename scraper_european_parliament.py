#!/usr/bin/env python3
import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from lxml import etree
from ftfy import fix_text
from langdetect import DetectorFactory, detect, LangDetectException
from datasets import Dataset
from huggingface_hub import HfApi, login
from tqdm import tqdm

# Ensure consistent language detection
DetectorFactory.seed = 0

# Credentials from environment
HF_USERNAME = os.environ.get("HF_USERNAME", "YOUR_HUGGINGFACE_USERNAME")
HF_TOKEN = os.environ.get("HF_TOKEN")

# Settings for each scraper
SCRAPERS = [
    {
        "name": "Adopted Texts",
        "start_url": "https://www.europarl.europa.eu/doceo/document/TA-5-1999-07-21-TOC_NL.html",
        "dataset_name": "Dutch-European-Parliament-Adopted-Texts",
        "collect_fn": "collect_adopted_urls",
        "fetch_fn": "fetch_adopted_text",
        "source_label": "European Parliament Adopted Texts"
    },
    {
        "name": "Minutes",
        "start_url": "https://www.europarl.europa.eu/doceo/document/PV-5-2003-05-12-TOC_NL.html",
        "dataset_name": "Dutch-European-Parliament-Minutes",
        "collect_fn": "collect_minutes_urls",
        "fetch_fn": "fetch_minutes_text",
        "source_label": "European Parliament Minutes"
    },
    {
        "name": "Verbatim Reports",
        "start_url": "https://www.europarl.europa.eu/doceo/document/CRE-4-1996-04-15-TOC_NL.html",
        "dataset_name": "Dutch-European-Parliament-Verbatim-Reports",
        "collect_fn": "collect_report_urls",
        "fetch_fn": "fetch_report_text",
        "source_label": "European Parliament Verbatim Report"
    }
]

# Common cleanup for HTML/XML content
def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    patterns = [
        r"\(The sitting (?:was suspended|opened|closed|ended) at.*?\)",
        r"\(Voting time ended at.*?\)",
        r"\((?:debat|stemming|vraag|interventie)\)",
        r"\(Het woord wordt gevoerd door:.*?\)",
        r"(\(|\[)\s*(?:(?:[a-zA-Z]{2,3})\s*(?:|\s|))?\s*(?:artikel|rule|punt|item)\s*\d+(?:,\s*lid\s*\d+)?\s*(?:\s+\w+)?\s*(\)|\])",
        r"\[(COM|A)\d+-\d+(/\d+)?\]",
        r"\(?:(?:http|https):\/\/[^\s]+?\)",
        r"\[\s*\d{4}/\d{4}\(COD\)\]",
        r"\[\s*\d{4}/\d{4}\(INI\)\]",
        r"\[\s*\d{4}/\d{4}\(RSP\)\]",
        r"\[\s*\d{4}/\d{4}\(IMM\)\]",
        r"\[\s*\d{4}/\d{4}\(NLE\)\]",
        r"\[\s*\d{5}/\d{4}\s*-\s*C\d+-\d+\/\d+\s*-\s*\d{4}/\d{4}\(NLE\)\]",
        r"\(\u201cStemmingsuitslagen\u201d, punt \d+\)",
        r"\(de Voorzitter(?: maakt na de toespraak van.*?| weigert in te gaan op.*?| stemt toe| herinnert eraan dat de gedragsregels moeten worden nageleefd| neemt er akte van|)\)",
        r"\(zie bijlage.*?\)",
        r"\(\s*De vergadering wordt om.*?geschorst\.\)",
        r"\(\s*De vergadering wordt om.*?hervat\.\)",
        r"Volgens de \u201ccatch the eye\u201d-procedure wordt het woord gevoerd door.*?\.",
        r"Het woord wordt gevoerd door .*?\.",
        r"De vergadering wordt om \d{1,2}\.\d{2} uur gesloten\.",
        r"De vergadering wordt om \d{1,2}\.\d{2} uur geopend\.",
        r"Het debat wordt gesloten\.",
        r"Stemming:.*?\.",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()

# Adopted Texts scraper
def collect_adopted_urls(start_url: str) -> list[str]:
    urls, visited = [], set()
    current = start_url
    session = requests.Session()
    while current and current not in visited:
        visited.add(current)
        resp = session.get(current, timeout=20)
        if resp.status_code == 404:
            # no fix logic here, skip
            break
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        urls.append(current.replace("-TOC", ""))
        next_link = soup.find("a", title="Volgende") or soup.find("a", string=re.compile("Volgende", re.I))
        if not next_link or not next_link.get("href"):
            break
        current = urljoin(current, next_link["href"])
    return urls

def extract_adopted_text(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    txt = clean_text("\n".join(paras))
    if not txt or len(txt) <= 50:
        return None
    if "deze tekst wordt nog verwerkt voor publicatie in uw taal" in txt.lower():
        return None
    return txt

# Minutes scraper
NAMESPACES = {"text": "http://openoffice.org/2000/text", "table": "http://openoffice.org/2000/table"}

def collect_minutes_urls(start_url: str) -> list[str]:
    urls, visited = [], set()
    current = start_url
    session = requests.Session()
    while current and current not in visited:
        visited.add(current)
        resp = session.get(current, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        urls.append(current.replace("-TOC_NL.html", "_NL.xml"))
        next_link = soup.find("a", title="Volgende") or soup.find("a", string=re.compile("Volgende", re.I))
        if not next_link or not next_link.get("href"):
            break
        current = urljoin(current, next_link["href"])
    return urls

def extract_minutes_from_xml(xml_bytes: bytes) -> str | None:
    try:
        root = etree.fromstring(xml_bytes, parser=etree.XMLParser(recover=True, ns_clean=True))
    except etree.XMLSyntaxError:
        return None
    texts = []
    sections = ["PV.Other.Text","PV.Debate.Text","PV.Vote.Text","PV.Sitting.Resumption.Text",
                "PV.Approval.Text","PV.Agenda.Text","PV.Sitting.Closure.Text"]
    for sec in sections:
        for p in root.xpath(f"//{sec}//text:p", namespaces=NAMESPACES):
            t = p.xpath("string()").strip()
            if not t or len(t) < 20:
                continue
            if p.xpath("ancestor::table:table", namespaces=NAMESPACES):
                continue
            texts.append(t)
    txt = clean_text("\n".join(texts))
    return txt if txt and len(txt) > 50 else None

def extract_minutes_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    txt = clean_text("\n".join(paras))
    return txt if txt and len(txt) > 50 else None

def fetch_minutes_text(url: str, session: requests.Session) -> str | None:
    resp = session.get(url, timeout=20)
    if resp.status_code == 404 and url.endswith("_NL.xml"):
        resp = session.get(url.replace("_NL.xml", "_NL.html"), timeout=20)
        resp.raise_for_status()
        return extract_minutes_from_html(resp.text)
    resp.raise_for_status()
    return extract_minutes_from_xml(resp.content)

# Verbatim Reports scraper
def collect_report_urls(start_url: str) -> list[str]:
    urls, visited = [], set()
    current = start_url
    session = requests.Session()
    while current and current not in visited:
        visited.add(current)
        resp = session.get(current, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        urls.append(current.replace("-TOC_NL.html", "_NL.html"))
        next_link = soup.find("a", title="Volgende") or soup.find("a", string=re.compile("Volgende", re.I))
        if not next_link or not next_link.get("href"):
            break
        current = urljoin(current, next_link["href"])
    return urls


def is_dutch(text: str) -> bool:
    try:
        return detect(text) == "nl"
    except LangDetectException:
        return False

def extract_report_from_xml(xml_bytes: bytes) -> str | None:
    try:
        root = etree.fromstring(xml_bytes, parser=etree.XMLParser(recover=True, ns_clean=True))
    except etree.XMLSyntaxError:
        return None
    nodes = root.xpath('//*[translate(@xml:lang, "NL", "nl")="nl" or translate(@lang, "NL", "nl")="nl"]')
    texts = ["".join(n.itertext()).strip() for n in nodes if n is not None]
    texts = [t for t in texts if t and is_dutch(t)]
    if not texts:
        return None
    txt = fix_text("\n".join(texts))
    return clean_text(txt) if txt and len(txt) > 50 else None

def extract_report_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p", class_="contents")]
    paras = [p for p in paras if is_dutch(p)]
    if not paras:
        tags = [t for t in soup.find_all(True) if t.get("lang","").lower().startswith("nl")]
        paras = [t.get_text(" ", strip=True) for t in tags if is_dutch(t.get_text())]
    if not paras:
        return None
    txt = fix_text("\n".join(paras))
    return clean_text(txt) if txt and len(txt) > 50 else None

def fetch_report_text(url: str, session: requests.Session) -> str | None:
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    ct = resp.headers.get("Content-Type","")
    if url.endswith(".xml") or "xml" in ct:
        return extract_report_from_xml(resp.content)
    return extract_report_from_html(resp.text)

# Runner and dataset push

def push_dataset(records: list[dict], repo_name: str) -> None:
    if not records:
        print(f"No records scraped for {repo_name}")
        return
    if not HF_TOKEN:
        print("HF_TOKEN not set")
        return
    login(token=HF_TOKEN)
    ds = Dataset.from_list(records)
    api = HfApi()
    repo_id = f"{HF_USERNAME}/{repo_name}"
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
    ds.push_to_hub(repo_id)


def main():
    for scraper in SCRAPERS:
        print(f"Running {scraper['name']} scraper...")
        collect = globals()[scraper['collect_fn']]
        fetch = globals()[scraper['fetch_fn']]
        urls = collect(scraper['start_url'])
        data = []
        with requests.Session() as session:
            for url in tqdm(urls, desc=f"Scraping {scraper['name']}"):
                try:
                    text = fetch(url, session)
                    if text:
                        data.append({"URL": url, "text": text, "source": scraper['source_label']})
                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
        push_dataset(data, scraper['dataset_name'])

if __name__ == "__main__":
    main()
