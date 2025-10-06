import streamlit as st
from src.services import scrape_and_store_product, fetch_and_store_competitors
from src.db import Database
from src.llm import analyze_competitors


def render_header():
    st.title("Amazon Competitor Analysis")
    st.caption("Enter your ASIN to get product insights.")


def render_inputs():
    asin = st.text_input("ASIN", placeholder="e.g., B0CX23VSAS")
    geo = st.text_input("Zip/Postal Code", placeholder="e.g., 83980")
    domain = st.selectbox("Domain", [
        "com", "ca", "co.uk", "de", "fr", "it", "ae"
    ])
    return asin.strip(), geo.strip(), domain


def render_product_card(product):
    with st.container(border=True):
        cols = st.columns([1, 2])

        try:
            images = product.get("images", [])
            if images and len(images) > 0:
                cols[0].image(images[0], width=200)
            else:
                cols[0].write("No image found.")
        except:
            cols[0].write("Error loading image")

        with cols[1]:
            st.subheader(product.get("title") or product["asin"])
            info_cols = st.columns(3)
            currency = product.get("currency", "")
            price = product.get("price", "-")
            info_cols[0].metric("Price", f"{currency} {price}" if currency else price)
            info_cols[1].write(f"Brand: {product.get('brand', '-')}")
            info_cols[2].write(f"Product: {product.get('product', '-')}")

            domain_info = f"amazon.{product.get('amazon_domain', 'com')}"
            geo_info = product.get("geo_location", "-")
            st.caption(f"Domain: {domain_info} | Geo Location: {geo_info}")

            st.write(product.get("url", ""))
            if st.button("Start analyzing competitors", key=f"analyze_{product['asin']}"):
                st.session_state["analyzing_asin"] = product["asin"]

def main():
    st.set_page_config(page_title="Amazon Competitor Analysis", page_icon="📚", layout="wide")
    render_header()
    asin, geo, domain = render_inputs()

    if st.button("Scrape Product") and asin:
        with st.spinner("Scraping product..."):
            scrape_and_store_product(asin, geo, domain)
        st.success("Product scraped successfully!")

    db = Database()
    products = db.get_all_products()
    if products:
        st.divider()
        st.subheader("Product Scraped")

        items_per_page = 10
        total_pages = (len(products) + items_per_page - 1) // items_per_page

        col1, col2, col2 = st.columns([2, 3, 2])
        with col2:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) -1

        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(products))

        st.write(f"Showing {start_idx + 1} - {end_idx} of {len(products)} products")

        for p in products[start_idx:end_idx]:
            render_product_card(p)

    selected_asin = st.session_state.get("analyzing_asin")
    if selected_asin:
        st.divider()
        st.subheader(f"Competitor analysis for {selected_asin}")

        db = Database()
        existing_comps = db.search_products({"parent_asin": selected_asin})

        if not existing_comps:
            with st.spinner("Searching..."):
                comps = fetch_and_store_competitors(selected_asin, domain, geo)

            st.success(f"Found {len(comps)} competitors!")
        else:
            st.info(f"Found {len(existing_comps)} existing competitors in the database.")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Refresh Competitors"):
                with st.spinner("Refreshing..."):
                    comps = fetch_and_store_competitors(selected_asin, domain, geo)
                st.success(f"Found {len(comps)} competitors!")

        with col1:
            if st.button("Analyze with LLM", type="primary"):
                with st.spinner("Running LLM..."):
                    analysis = analyze_competitors(db, selected_asin)
                    st.markdown(analysis)


if __name__ == "__main__":
    main()