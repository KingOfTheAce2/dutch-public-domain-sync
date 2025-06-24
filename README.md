
Dutch European Parliament Scrapers

This repository contains a combined Python script that scrapes three categories of Dutch-language content from the European Parliament website:

- Adopted Texts
- Verbatim Reports
- Minutes

Each scraper navigates the Parliament's archive via "Volgende" (Next) links and extracts relevant text content. The cleaned data is pushed to the Hugging Face Hub under your account.

---

📘 Adopted Texts

Starting URL:
https://www.europarl.europa.eu/doceo/document/TA-5-1999-07-21-TOC_NL.html

- Follows chronological navigation through “Volgende” links.
- Extracts content by removing `-TOC` from the page URL.
- Automatically corrects malformed URLs that include invalid term numbers (e.g. `TA-0-...`) based on the date.
- Outputs data to: vGassen/Dutch-European-Parliament-Adopted-Texts.

---

🗣️ Verbatim Reports

Starting URL:
https://www.europarl.europa.eu/doceo/document/CRE-4-1996-04-15-TOC_NL.html

- Navigates using “Volgende” links.
- Drops `-TOC` from URLs to access full documents.
- Parses HTML or XML for content, and filters paragraphs using `langdetect` to retain only Dutch text.
- Outputs data to: vGassen/Dutch-European-Parliament-Verbatim-Reports.

---

📝 Minutes

Starting URL:
https://www.europarl.europa.eu/doceo/document/PV-5-2003-05-12-TOC_NL.html

- Navigates forward using “Volgende”.
- Downloads XML format where available, falling back to HTML.
- Extracts sections such as debates, votes, and agendas.
- Outputs data to: vGassen/Dutch-European-Parliament-Minutes.

---

🔧 Usage

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

🛠️ Automation

If you want to automate the script with GitHub Actions, set the HF_USERNAME and HF_TOKEN as repository secrets. This will enable periodic scraping and automatic uploads to the Hugging Face Hub.

---

⚖️ License

This code is released under the MIT License. 

# Note that the scraped content is subject to the European Parliament's reuse policy:
https://www.europarl.europa.eu/legal-notice/en/#reuse
