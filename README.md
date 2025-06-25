# European Parliament Dutch Language Scrapers

This repository contains a combined Python script that scrapes three categories of Dutch-language content from the European Parliament website:

- Adopted Texts
- Verbatim Reports
- Minutes

Each scraper navigates the Parliament's archive via "Volgende" (Next) links and extracts relevant text content. The cleaned data is pushed to the Hugging Face Hub under your account.

**Status: Work in Progress**

Additional datasets are planned for inclusion. The tables below list the collections that will be added.

### European Union

| Collection | Location | GitHub |
|------------|----------|--------|
| Curia (WIP) | <https://curia.europa.eu/jcms/jcms/Jo2_7045/nl/> | |
| European Parliament  Minutes | ? | <https://github.com/KingOfTheAce2/Euro-Parl-Minute-Scraper-Test> |
| European Parliament  Adopted Texts | ? | <https://github.com/KingOfTheAce2/Euro-Parl-Adopted-Texts-Scraper> |
| European Parliament Verbatim Report | ? | <https://github.com/KingOfTheAce2/Euro-Parl-Verbatim-Report-Scraper> |

### Netherlands

| Collection | Location | GitHub |
|------------|----------|--------|
| Rechtspraak (WIP) | <https://www.rechtspraak.nl/Uitspraken/Paginas/Open-Data.aspx> | <https://github.com/KingOfTheAce2/rechtspraak-sync> |
| Officiële publicates (WIP) | <https://repository.overheid.nl/frbr/> | <https://github.com/KingOfTheAce2/Dutch-Lokale-Bekendmakingen-Sync> |
| Samenwerkende Catalogi (not started) | <https://repository.overheid.nl/frbr/> | |
| Statengeneraal Digitaal (WIP) | <https://repository.overheid.nl/frbr/> | <https://github.com/KingOfTheAce2/Statengeneraal-Digitaal-scraper> |
| Tuchtrecht (WIP) | <https://repository.overheid.nl/frbr/> | <https://github.com/KingOfTheAce2/Dutch-Disciplinary-Law-Tuchtrecht> |
| Verdragenbank (not started) | <https://repository.overheid.nl/frbr/> | |
| PLOOI (not started) | <https://repository.overheid.nl/frbr/> | |
| CVDR (not started) | <https://zoekservice.overheid.nl/> | |
| Basiswettenbestand (WIP) | <https://zoekservice.overheid.nl/> | |
| Europese Ricthlijnen (not started) | <https://zoekservice.overheid.nl/> | |
| PUC Open Data (not started) | <https://zoekservice.overheid.nl/> | |
| Wetgevingskalender (not started) | <https://zoekservice.overheid.nl/> | |
| Staatsalmanak (not started) | <https://zoekservice.overheid.nl/> | |

---

# 📘 Adopted Texts

Starting URL:
https://www.europarl.europa.eu/doceo/document/TA-5-1999-07-21-TOC_NL.html

- Follows chronological navigation through “Volgende” links.
- Extracts content by removing `-TOC` from the page URL.
- Automatically corrects malformed URLs that include invalid term numbers (e.g. `TA-0-...`) based on the date.
- Outputs data to: vGassen/Dutch-European-Parliament-Adopted-Texts.

---

# 🗣️ Verbatim Reports

Starting URL:
https://www.europarl.europa.eu/doceo/document/CRE-4-1996-04-15-TOC_NL.html

- Navigates using “Volgende” links.
- Drops `-TOC` from URLs to access full documents.
- Parses HTML or XML for content, and filters paragraphs using `langdetect` to retain only Dutch text.
- Outputs data to: vGassen/Dutch-European-Parliament-Verbatim-Reports.

---

# 📝 Minutes

Starting URL:
https://www.europarl.europa.eu/doceo/document/PV-5-2003-05-12-TOC_NL.html

- Navigates forward using “Volgende”.
- Downloads XML format where available, falling back to HTML.
- Extracts sections such as debates, votes, and agendas.
- Outputs data to: vGassen/Dutch-European-Parliament-Minutes.

---

# 🔧 Usage

Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

Install and Run

pip install -r requirements.txt

# Set credentials for Hugging Face
export HF_USERNAME=<your_username>
export HF_TOKEN=<your_token>

# Run the scraper
python scraper_european_parliament.py

Each dataset will be created or updated on Hugging Face Hub under your username.

---

# 🛠️ Automation

If you want to automate the script with GitHub Actions, set the HF_USERNAME and HF_TOKEN as repository secrets. This will enable periodic scraping and automatic uploads to the Hugging Face Hub.

---

# ⚖️ License

This code is released under the MIT License. 

Note that the scraped content is subject to the European Parliament's reuse policy:
https://www.europarl.europa.eu/legal-notice/en/#reuse
