# Amazon Competitor Analyzer

A Streamlit app that scrapes Amazon product data, finds similar listings, and generates an LLM-backed competitor analysis.

Enter an [ASIN](https://en.wikipedia.org/wiki/Amazon_Standard_Identification_Number), marketplace, and zip/postal code. The app fetches product details via [Oxylabs](https://oxylabs.io/), stores them locally, searches for competitors, and can summarize positioning, pricing, and recommendations with GPT-4.

## Features

- Scrape a product by ASIN across Amazon marketplaces (`.com`, `.ca`, `.co.uk`, `.de`, `.fr`, `.it`, `.ae`)
- Search and scrape competing listings using title, category, and sort strategies
- Persist products in a local [TinyDB](https://tinydb.readthedocs.io/) JSON store
- Generate competitor insights (summary, positioning, top competitors, recommendations)

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An [Oxylabs](https://oxylabs.io/) Web Scraper API account
- An [OpenAI](https://platform.openai.com/) API key (for competitor analysis)

## Setup

```bash
git clone https://github.com/zott1991/amazon-competitor-analyzer.git
cd amazon-competitor-analyzer
uv sync
```

Create a `.env` file in the project root:

```env
OXYLABS_USERNAME=your_oxylabs_username
OXYLABS_PASSWORD=your_oxylabs_password
OPENAI_API_KEY=your_openai_api_key
```

## Run

```bash
uv run streamlit run main.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

### Usage

1. Enter an ASIN, zip/postal code, and Amazon domain.
2. Click **Scrape Product** to fetch and store the listing.
3. Click **Start analyzing competitors** on a product card to search similar listings.
4. Click **Analyze with LLM** for a written comparison of the product vs. its competitors.

Scraped products are stored in `data.json` in the project root.

## Project structure

```
main.py                 Streamlit UI
src/
  oxylabs_client.py     Oxylabs API client (product + search scrape)
  services.py           Scrape/store orchestration
  db.py                 TinyDB product storage
  llm.py                GPT-4 competitor analysis
```
