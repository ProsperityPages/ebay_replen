import streamlit as st
import pandas as pd
import requests
import json
import os
import time

# --- PAGE SETTINGS ---
st.set_page_config(
    page_title="Replen Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_FILE = "replens_db.json"

EBAY_OAUTH_TOKEN = "v^1.1#i^1#f^0#r^0#p^1#I^3#t^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"
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
# NEW:
ebay_token = st.sidebar.text_input("eBay OAuth Token", value=EBAY_OAUTH_TOKEN, type="password")
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
