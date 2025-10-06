import json
import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OXYLABS_BASE_URL = "https://realtime.oxylabs.io/v1/queries"


def extract_content(payload):
    if isinstance(payload, dict):
        if "results" in payload and isinstance(payload["results"], list) and payload["results"]:
            first = payload["results"][0]
            if isinstance(first, dict) and "content" in first:
                return first["content"] or {}
        if "content" in payload:
            return payload.get("content", {})

    return payload


def post_query(payload):
    username = os.getenv("OXYLABS_USERNAME")
    password = os.getenv("OXYLABS_PASSWORD")

    response = requests.post(OXYLABS_BASE_URL, auth=(username, password), json=payload)
    response.raise_for_status()
    response_json = response.json()

    return response_json


def normalize_product(content):
    category_path = []
    if content.get("category_path"):
        category_path = [cat.strip() for cat in content["category_path"] if cat]

    return {
        "asin": content.get("asin"),
        "url": content.get("url"),
        "brand": content.get("brand"),
        "price": content.get("price"),
        "stock": content.get("stock"),
        "title": content.get("title"),
        "rating": content.get("rating"),
        "images": content.get("images", []),
        "categories": content.get("category", []) or content.get("categories", []),
        "category_path": category_path,
        "currency": content.get("currency"),
        "buybox": content.get("buybox", []),
        "product_overview": content.get("product_overview", []),
    }


def scrape_product_details(asin, geo_location, domain):
    payload = {
        "source": "amazon_product",
        "query": asin,
        "geo_location": geo_location,
        "domain": domain,
        "parse": True
    }
    raw = post_query(payload)
    content = extract_content(raw)
    normalized = normalize_product(content)
    if not normalized.get("asin"):
        normalized["asin"] = asin

    normalized["amazon_domain"] = domain
    normalized["geo_location"] = geo_location
    return normalized


def clean_product_name(title):
    if "-" in title:
        title = title.split("-")[0]
    if "|" in title:
        title = title.split("|")[0]
    return title.strip()


def extract_search_results(content):
    items = []
    if not isinstance(content, dict):
        return items

    if "results" in content:
        results = content["results"]
        if isinstance(results, dict):
            if "organic" in results:
                items.extend(results["organic"])
            if "paid" in results:
                items.extend(results["paid"])
    elif "products" in content and isinstance(content["products", list]):
        items.extend(content["products"])

    return items


def normalize_search_result(item):
    asin = item.get("asin") or item.get("product_asin")
    title = item.get("title")

    if not (asin or title):
        return None

    return {
        "asin": asin,
        "title": title,
        "category": item.get("category"),
        "price": item.get("price"),
        "rating": item.get("rating")
    }


def search_competitors(query_title, domain, categories, pages=1, geo_location=""):
    st.write("🔎 Searching for competitors")

    search_title = clean_product_name(query_title)
    results = []
    seen_asins = set()

    strategies = ["featured", "price_asc", "price_desc", "avg_rating"]

    for sort_by in strategies:
        for page in range(1, max(1, pages) + 1):
            payload = {
                "source": "amazon_search",
                "query": search_title,
                "parse": True,
                "domain": domain,
                "page": page,
                "sort_by": sort_by,
                "geo_location": geo_location
            }

            if categories and categories[0]:
                payload["refinements"] = {"category": categories[0]}

            content = extract_content(post_query(payload))
            items = extract_search_results(content)

            for item in items:
                result = normalize_search_result(item)
                if result and result["asin"] not in seen_asins:
                    seen_asins.add(result["asin"])
                    results.append(result)

            time.sleep(0.1)

    st.write(f"✅ Found {len(results)} competitors")
    return results


def scrape_multiple_products(asins, geo_location, domain):
    st.write("🔎 Scraping details")
    products = []

    progress_text = st.empty()
    progress_bar = st.progress(0)
    total = len(asins)

    for idx, a in enumerate(asins, 1):
        try:
            progress_text.write(f"Processing competitor {idx}/{total}: {a}")
            progress_bar.progress(idx / total)

            product = scrape_product_details(a, geo_location, domain)
            products.append(product)
            progress_text.write(f"✅ Found: {product.get('title', a)}")
        except Exception as e:
            progress_text.write(f"❌ Failed to scrape {a}")
            continue
        time.sleep(0.1)

    progress_text.empty()
    progress_bar.empty()

    st.write(f"✅ Successfully scraped {len(products)} out of {total} competitors")
    return products