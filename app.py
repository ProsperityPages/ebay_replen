import streamlit as st
import pandas as pd
import requests
import json
import os
import time

EBAY_OAUTH_TOKEN = "v^1.1#i^1#p^1#r^0#f^0#I^3#t^H4sIAAAAAAAA/+VYe2wURRjv9YFWwAqiFUU4VoiR5vbm3nsb7uK1UHtCudIrLW2AZnZ3tl26t3vdmaW9EEzTCBHTxAY1RNHYihAxMZH4TtAYQhWNJgSFYBQwMSGo5SEvJfE196BcK4HSntrE+2dvZr7vm+/7zfeaAV2Tihdsqtr0y1TLLfl9XaAr32JxTAbFk4rKbi/Iv7coD2QRWPq65nUVdhecXIhhTI3ztQjHdQ0ja2dM1TCfmgwwpqHxOsQK5jUYQ5gnIh8NVS/lnSzg44ZOdFFXGWt4UYBxicDpAwLw+DwISX4fndWuyKzTA4wEBJ8gCF4R+mXZ5/HSdYxNFNYwgRoJME7g9NoAZ3P664CPd3A84FiP39vEWOuRgRVdoyQsYIIpdfkUr5Gl6/VVhRgjg1AhTDAcqoxGQuFFi5fVLbRnyQpmcIgSSEw8fFShS8haD1UTXX8bnKLmo6YoIowZezC9w3ChfOiKMmNQPwW1DL1ut9ONKJwydAF3TqCs1I0YJNfXIzmjSDY5RcojjSgkcSNEKRrCWiSSzGgZFRFeZE1+lptQVWQFGQFmcXmoMVRTwwRrDB3HkaHYhv5Ey1faPG43J7o5v8vGSRBxHiRlNkpLy8A8YqcKXZOUJGjYukwn5YhqjUZiA7KwoUQRLWKEZJLUKJvOfwVDztGUPNT0KZqkVUueK4pRIKyp4Y1PYIibEEMRTIKGJIxcSEEUYGA8rkjMyMWUL2bcpxMHmFZC4rzd3tHRwXa4WN1osTsBcNhXVi+Niq0oBhlKm4z1NL1yYwabkjJFRJQTKzxJxKkundRXqQJaCxP0AA64QQb34WoFR87+bSLLZvvwiMhVhIhuCXAycAkur0f2Ol25iJBgxkntST2QABO2GDTaEImrUEQ2kfqZGaMOK/Euj+x0cTKySV6/bHPTdGcTPJLX5pARAohGrejn/k+BMlpXjyLRQCQnvp4zP3cLiWhD63Kvy1PTtE5v1X2NIqlslPV2g7M7G6t0LVIll4U7cb20IjDaaLim8RWqQpGpo/vnAoBkrOcOhCodkyFPGpt5UVGPoxpdVcTExDpglyHVQIMkys0EHUeRqtLPuEwNxePh3GTsnBl5k8libHbnrlL9R1XqmlbhpONOLKuS/JgKgHGFpXUoGesJVtRjdh3SJiQ53ZzS2jqC8JpEdsFMsC0mwoRqItE+cNRMCk3mLC1p0uhZ0gWTGjF6FnrJkEyRjGmjVGVmKZpKSyvBN7Vn53hAEUy1bfQsEoLq6KjpHO0wqElJMAQotrEGgpKuqYlxubhCryoTysGpnWkQFCl9x2BTSLB4nUgtxrpJMcBsJNly1+ltSKMNDDF0VUVGvWPcqTsWMwkUVDTRcngql9FYLxlfPlPgBOuwHD7O5+d8HMeNyy4x1T81T7QK9K9U3lqaQWITy24MNUnQO/+BC6J9+HNVMC/1c3RbPgXdloF8iwVUAJujDDw0qWBFYcEUBtOUzGbUYRUos7QaaJCYBmLbUCIOFSN/eqkxGHrmvkrz7b028vrKrXV5t2U9mvWtBvcMPZsVFzgmZ72hgVlXV4ocJaVTnV7AOf3A5+AA1wQeuLpa6Li7cEZ1e2RXbeybgZ/nH+088N3gb+u3bDkEpg4RWSxFeYXdlrzVp95YS3qe2N80e2P7l4PTit+5tP6FplWHD/aCVY9tsi+56/Kv6/p7ms9uKCM7jMdnBvXnDsITP4a3Prp8QfD3khNP/rHtzJGTfepluG/nvO7SgtP9Z4M1cx7pmD/w1B1v9Zbsf750c8VGrzP4wfn1Gy4k2i88fGfBn8d+uFUv/d46ffDS4ahD+Pq1+jVwz4yGrjnT9hxRV+15ZR9o+Chy7OKS1ZGf1vR+PjfWcvyTr3Z3P3iurf9w5FLzuy/ObdhVfca68/zLS2dMOXigbrvWTPqfDn8cn/ZZ+Zu+jpln3m++/+Je57Pbjh9t2X16+6trN9d+eA6f7nUMxGZHZpX02CaT4z07XlrS94WDfHvqvUPpI/0Lb0RwFs4UAAA="
# Leave type="password" exactly as written so it hides the token characters on screen
ebay_token = st.sidebar.text_input("eBay OAuth Token", value=EBAY_OAUTH_TOKEN, type="password")
# --- PAGE SETTINGS ---
st.set_page_config(
    page_title="Replen Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_FILE = "replens_db.json"

# --- PERSISTENCE HELPERS ---
def load_replens():
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return [
        {
            "asin": "B08N5WRWNW",
            "title": "Sony WH-1000XM4 Wireless Headphones",
            "target_price": 130.0,
            "amazon_price": 248.0,
            "conditions": ["USED", "NEW"],
            "allow_best_offer": True,
            "tag": "Electronics",
            "notes": "Target 40%+ ROI"
        },
        {
            "asin": "0321743261",
            "title": "Calculus: Early Transcendentals",
            "target_price": 40.0,
            "amazon_price": 125.0,
            "conditions": ["USED"],
            "allow_best_offer": True,
            "tag": "Textbooks",
            "notes": "August/Jan Season Flip"
        }
    ]

def save_replens(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "replens" not in st.session_state:
    st.session_state.replens = load_replens()

# --- NOTIFICATION ENGINE ---
def send_push_alert(topic, title, price, target, link):
    if not topic:
        return
    endpoint = f"https://ntfy.sh/{topic}"
    headers = {
        "Title": f"🎯 Replen Caught: ${price:.2f} (Target: ${target:.2f})",
        "Priority": "high",
        "Tags": "moneybag,package",
        "Click": link
    }
    msg = f"Item: {title}\nBuy Price: ${price:.2f}\nTarget: ${target:.2f}"
    try:
        requests.post(endpoint, data=msg.encode("utf-8"), headers=headers, timeout=4)
    except Exception:
        pass

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ Sourcing Engine")
ebay_token = st.sidebar.text_input("eBay OAuth Token", type="password", placeholder="Bearer token...")
ntfy_topic = st.sidebar.text_input("iOS Push Topic (ntfy.sh)", value="my-replen-alerts-2026")
default_fee_pct = st.sidebar.slider("Estimated Amazon / FBA Fee (%)", 10, 25, 15)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Add this URL to your iPhone Home Screen via Safari Share to use it as a native iOS app.")

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Monitored Replens", len(st.session_state.replens))
avg_target = sum([r["target_price"] for r in st.session_state.replens]) / max(len(st.session_state.replens), 1)
col2.metric("Avg Target Buy Price", f"${avg_target:.2f}")
avg_spread = sum([r.get("amazon_price", 0) - r["target_price"] for r in st.session_state.replens]) / max(len(st.session_state.replens), 1)
col3.metric("Avg Target Spread", f"${avg_spread:.2f}")
col4.metric("Stream Status", "🟢 Live" if ebay_token else "🟡 Mock Mode")

st.divider()

# --- APP TABS ---
tab_feed, tab_manage, tab_calc = st.tabs(["⚡ Live Stream Sourcing", "📋 Replens Manager", "🧮 Fast Flip Calculator"])

# ==========================================
# 1. LIVE STREAM FEED (ReplenCatcher Style)
# ==========================================
with tab_feed:
    st.subheader("Live Deal Sourcing Stream")

    def fetch_ebay_listings(replen):
        if not ebay_token:
            # Mock listing for demonstration if no API key is provided
            return [{
                "itemId": f"demo_{replen['asin']}",
                "title": f"{replen['title']} - In Box Clean",
                "price": {"value": f"{replen['target_price'] * 0.88:.2f}", "currency": "USD"},
                "condition": "Used",
                "itemWebUrl": "https://www.ebay.com",
                "buyingOptions": ["FIXED_PRICE", "BEST_OFFER"] if replen["allow_best_offer"] else ["FIXED_PRICE"]
            }]

        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {"Authorization": f"Bearer {ebay_token}", "Content-Type": "application/json"}
        params = {"q": replen["title"], "sort": "newlyListed", "limit": "3"}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=5)
            if r.status_code == 200:
                return r.json().get("itemSummaries", [])
        except Exception:
            pass
        return []

    stream_grid = st.columns(2)
    deals_count = 0

    for idx, replen in enumerate(st.session_state.replens):
        listings = fetch_ebay_listings(replen)
        for item in listings:
            price = float(item["price"]["value"])
            if price <= replen["target_price"]:
                deals_count += 1
                with stream_grid[deals_count % 2]:
                    with st.container(border=True):
                        # Title and Tag
                        st.markdown(f"**[{replen.get('tag', 'Replen')}]** `{replen['asin']}`")
                        st.markdown(f"##### 🎯 {item['title'][:70]}...")

                        # Pricing columns
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"**eBay Price:** :green[**${price:.2f}**]")
                        c2.markdown(f"**Amazon Sell:** ${replen['amazon_price']:.2f}")

                        # Profit math
                        est_fees = replen['amazon_price'] * (default_fee_pct / 100.0)
                        net_profit = replen['amazon_price'] - price - est_fees
                        roi = (net_profit / price) * 100 if price > 0 else 0
                        c3.markdown(f"**Net Margin:** :blue[**+${net_profit:.2f}**] ({roi:.0f}%)")

                        st.caption(f"Condition: {item.get('condition', 'Used')} | Best Offer: {'Yes' if 'BEST_OFFER' in item.get('buyingOptions', []) else 'No'}")

                        # Action Buttons
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        btn_col1.link_button("🛒 View eBay", item.get("itemWebUrl", "https://www.ebay.com"), use_container_width=True)
                        btn_col2.link_button("📈 Keepa", f"https://keepa.com/#!product/1-{replen['asin']}", use_container_width=True)
                        btn_col3.link_button("🔍 SellerAmp", f"https://sas.selleramp.com/sas/lookup?search_term={replen['asin']}", use_container_width=True)

    if deals_count == 0:
        st.info("No newly listed items under your target buy price. Stream is actively listening.")

# ==========================================
# 2. REPLENS MANAGER (Add/Edit/Delete)
# ==========================================
with tab_manage:
    st.subheader("Manage Replen Watchlist")

    with st.expander("➕ Add New ASIN / Replen Target", expanded=False):
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            f_asin = f1.text_input("Amazon ASIN / ISBN", placeholder="e.g. B08N5WRWNW")
            f_title = f2.text_input("Search Title / Keywords", placeholder="e.g. Sony WH-1000XM4")

            f3, f4, f5 = st.columns(3)
            f_target = f3.number_input("Max Buy Price ($)", min_value=1.0, value=30.0, step=1.0)
            f_amazon = f4.number_input("Est. Amazon Sell Price ($)", min_value=1.0, value=85.0, step=1.0)
            f_tag = f5.text_input("Custom Tag", placeholder="e.g. Video Games")

            f_cond = st.multiselect("Allowed Conditions", ["USED", "NEW"], default=["USED", "NEW"])
            f_bo = st.checkbox("Include Best Offer Listings", value=True)
            f_notes = st.text_input("Custom Strategy Notes", placeholder="e.g. Check for missing cables")

            if st.form_submit_button("Add Replen to Monitor"):
                if f_title.strip():
                    new_item = {
                        "asin": f_asin.strip() or "N/A",
                        "title": f_title.strip(),
                        "target_price": float(f_target),
                        "amazon_price": float(f_amazon),
                        "conditions": f_cond,
                        "allow_best_offer": f_bo,
                        "tag": f_tag.strip() or "General",
                        "notes": f_notes
                    }
                    st.session_state.replens.append(new_item)
                    save_replens(st.session_state.replens)
                    st.success(f"Added {f_title} to live monitoring!")
                    st.rerun()

    # Table View
    if st.session_state.replens:
        df = pd.DataFrame(st.session_state.replens)
        st.dataframe(
            df[["tag", "asin", "title", "target_price", "amazon_price", "notes"]],
            column_config={
                "tag": "Tag",
                "asin": "ASIN",
                "title": "Title / Keywords",
                "target_price": st.column_config.NumberColumn("Target Buy ($)", format="$%.2f"),
                "amazon_price": st.column_config.NumberColumn("Amazon Sell ($)", format="$%.2f"),
                "notes": "Notes"
            },
            use_container_width=True,
            hide_index=True
        )

        del_title = st.selectbox("Select Replen to Delete", [r["title"] for r in st.session_state.replens])
        if st.button("🗑️ Delete Selected Replen"):
            st.session_state.replens = [r for r in st.session_state.replens if r["title"] != del_title]
            save_replens(st.session_state.replens)
            st.success(f"Removed {del_title}")
            st.rerun()

# ==========================================
# 3. FAST FLIP CALCULATOR
# ==========================================
with tab_calc:
    st.subheader("Fast Flip Margin & ROI Calculator")
    c1, c2, c3 = st.columns(3)
    in_buy = c1.number_input("Purchase Price ($)", value=35.0)
    in_sell = c2.number_input("Expected Amazon Sale Price ($)", value=95.0)
    in_fees = c3.slider("Platform / Shipping / FBA Fees (%)", 5, 30, 15)

    fee_total = in_sell * (in_fees / 100.0)
    net_profit = in_sell - in_buy - fee_total
    roi = (net_profit / in_buy) * 100 if in_buy > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Est. Net Profit", f"${net_profit:.2f}", delta=f"{roi:.1f}% ROI")
    m2.metric("Total Fees", f"${fee_total:.2f}")
    m3.metric("Net Margin", f"{(net_profit / in_sell) * 100:.1f}%")
