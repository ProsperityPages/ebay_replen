Python
import streamlit as st
import pandas as pd
import requests
import json
import os
import base64
import urllib.parse
import time

# --- PAGE CONFIGURATION ---
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
            "asin": "0321743261",
            "title": "Calculus Early Transcendentals",
            "target_price": 40.0,
            "amazon_price": 125.0,
            "condition": "USED",
            "best_offer_only": False,
            "tag": "Textbooks",
            "notes": "August/Jan Season Flip"
        },
        {
            "asin": "B08N5WRWNW",
            "title": "Sony WH-1000XM4",
            "target_price": 130.0,
            "amazon_price": 248.0,
            "condition": "ANY",
            "best_offer_only": False,
            "tag": "Electronics",
            "notes": "Target 40%+ ROI"
        }
    ]

def save_replens(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "replens" not in st.session_state:
    st.session_state.replens = load_replens()

# --- AUTO TOKEN REFRESH ENGINE ---
def get_oauth_token_from_credentials(client_id, client_secret):
    """Generates a fresh production OAuth token using eBay Client Credentials."""
    if not client_id or not client_secret:
        return None
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    auth_str = f"{client_id.strip()}:{client_secret.strip()}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=8)
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass
    return None

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ API Configuration")
auth_mode = st.sidebar.radio("Authentication Method", ["Auto-Generate (App ID + Cert ID)", "Manual Bearer Token"])

active_token = None

if auth_mode == "Auto-Generate (App ID + Cert ID)":
    st.sidebar.caption("Auto-refreshes every 2 hours so your app never disconnects.")
    app_id = st.sidebar.text_input("eBay App ID (Client ID)", type="password")
    cert_id = st.sidebar.text_input("eBay Cert ID (Client Secret)", type="password")
    if app_id and cert_id:
        active_token = get_oauth_token_from_credentials(app_id, cert_id)
        if active_token:
            st.sidebar.success("🟢 Authenticated & Auto-Refreshing")
        else:
            st.sidebar.error("🔴 Invalid App ID or Cert ID")
else:
    manual_token = st.sidebar.text_area("eBay OAuth Bearer Token", placeholder="v^1.1#...", height=100)
    if manual_token.strip():
        active_token = manual_token.strip()

default_fee_pct = st.sidebar.slider("Estimated Amazon / FBA Fee (%)", 10, 25, 15)
include_shipping = st.sidebar.checkbox("Factor Shipping Cost into Buy Price", value=True)

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Monitored Replens", len(st.session_state.replens))
avg_target = sum([r["target_price"] for r in st.session_state.replens]) / max(len(st.session_state.replens), 1)
col2.metric("Avg Target Buy Price", f"${avg_target:.2f}")
avg_spread = sum([r.get("amazon_price", 0) - r["target_price"] for r in st.session_state.replens]) / max(len(st.session_state.replens), 1)
col3.metric("Avg Target Spread", f"${avg_spread:.2f}")
col4.metric("Stream Status", "🟢 Live (Official API)" if active_token else "🟡 Mock Mode (Waiting for Token)")

st.divider()

# --- APP TABS ---
tab_feed, tab_manage, tab_calc = st.tabs(["⚡ Live Stream Sourcing", "📋 Replens Manager", "🧮 Fast Flip Calculator"])

# ==========================================
# 1. LIVE STREAM FEED
# ==========================================
with tab_feed:
    st.subheader("Live Deal Sourcing Stream")

    def fetch_ebay_official(replen, token):
        query_str = urllib.parse.quote_plus(replen["title"])
        search_link = f"https://www.ebay.com/sch/i.html?_nkw={query_str}"
        
        if not token:
            return [{
                "itemId": f"demo_{replen['asin']}",
                "title": f"[DEMO] {replen['title']} - Like New Clean",
                "price": {"value": f"{replen['target_price'] * 0.85:.2f}", "currency": "USD"},
                "shippingOptions": [{"shippingCost": {"value": "0.00"}}],
                "condition": "Used",
                "itemWebUrl": search_link,
                "buyingOptions": ["FIXED_PRICE", "BEST_OFFER"]
            }]

        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
        }
        params = {
            "q": replen["title"],
            "sort": "newlyListed",
            "limit": "4"
        }
        
        if replen.get("condition") == "NEW":
            params["filter"] = "conditions:{NEW}"
        elif replen.get("condition") == "USED":
            params["filter"] = "conditions:{USED}"

        try:
            r = requests.get(url, headers=headers, params=params, timeout=6)
            if r.status_code == 200:
                return r.json().get("itemSummaries", [])
        except Exception:
            pass
        return []

    stream_grid = st.columns(2)
    deals_count = 0

    for idx, replen in enumerate(st.session_state.replens):
        listings = fetch_ebay_official(replen, active_token)
        for item in listings:
            list_price = float(item.get("price", {}).get("value", 0.0))
            
            ship_cost = 0.0
            if "shippingOptions" in item and len(item["shippingOptions"]) > 0:
                ship_cost_str = item["shippingOptions"][0].get("shippingCost", {}).get("value", "0.0")
                try:
                    ship_cost = float(ship_cost_str)
                except ValueError:
                    ship_cost = 0.0
            
            total_buy_price = list_price + (ship_cost if include_shipping else 0.0)
            
            buying_opts = item.get("buyingOptions", [])
            if replen.get("best_offer_only") and "BEST_OFFER" not in buying_opts:
                continue

            if total_buy_price <= replen["target_price"] and total_buy_price > 0:
                deals_count += 1
                with stream_grid[deals_count % 2]:
                    with st.container(border=True):
                        st.markdown(f"**[{replen.get('tag', 'Replen')}]** `{replen.get('asin', 'N/A')}`")
                        st.markdown(f"##### 🎯 {item['title'][:70]}...")

                        c1, c2, c3 = st.columns(3)
                        ship_text = f"+${ship_cost:.2f} ship" if ship_cost > 0 else "Free ship"
                        c1.markdown(f"**eBay Buy:** :green[**${total_buy_price:.2f}**] \n\n*({ship_text})*")
                        c2.markdown(f"**Amazon Sell:** ${replen['amazon_price']:.2f}")

                        est_fees = replen['amazon_price'] * (default_fee_pct / 100.0)
                        net_profit = replen['amazon_price'] - total_buy_price - est_fees
                        roi = (net_profit / total_buy_price) * 100 if total_buy_price > 0 else 0
                        c3.markdown(f"**Net Profit:** :blue[**+${net_profit:.2f}**] ({roi:.0f}%)")

                        st.caption(f"Condition: **{item.get('condition', 'Used')}** | Best Offer: **{'Yes' if 'BEST_OFFER' in buying_opts else 'No'}**")

                        # Direct Search Fallback Fix
                        query_enc = urllib.parse.quote_plus(replen["title"])
                        direct_search_url = f"https://www.ebay.com/sch/i.html?_nkw={query_enc}"
                        target_url = item.get("itemWebUrl") or direct_search_url
                        if target_url == "https://www.ebay.com":
                            target_url = direct_search_url

                        btn1, btn2, btn3 = st.columns(3)
                        btn1.link_button("🛒 View eBay", target_url, use_container_width=True)
                        btn2.link_button("📈 Keepa", f"https://keepa.com/#!product/1-{replen['asin']}", use_container_width=True)
                        btn3.link_button("🔍 SellerAmp", f"https://sas.selleramp.com/sas/lookup?search_term={replen['asin']}", use_container_width=True)

    if deals_count == 0:
        st.info("No active newly listed items under your target buy price right now.")

# ==========================================
# 2. REPLENS MANAGER
# ==========================================
with tab_manage:
    st.subheader("Manage Replen Watchlist")

    with st.expander("➕ Add New ASIN / Replen Target", expanded=False):
        with st.form("add_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            f_asin = f1.text_input("Amazon ASIN / ISBN", placeholder="e.g. 0321743261")
            f_title = f2.text_input("Search Title / Keywords", placeholder="e.g. Calculus Early Transcendentals")

            f3, f4, f5 = st.columns(3)
            f_target = f3.number_input("Max Buy Price ($)", min_value=1.0, value=30.0, step=1.0)
            f_amazon = f4.number_input("Est. Amazon Sell Price ($)", min_value=1.0, value=85.0, step=1.0)
            f_tag = f5.text_input("Custom Tag", placeholder="e.g. Textbooks")

            f6, f7 = st.columns(2)
            f_cond = f6.selectbox("Condition Filter", ["ANY", "USED", "NEW"])
            f_bo = f7.checkbox("Require Best Offer", value=False)
            f_notes = st.text_input("Custom Strategy Notes", placeholder="e.g. Check for missing access codes")

            if st.form_submit_button("Add Replen to Monitor"):
                if f_title.strip():
                    new_item = {
                        "asin": f_asin.strip() or "N/A",
                        "title": f_title.strip(),
                        "target_price": float(f_target),
                        "amazon_price": float(f_amazon),
                        "condition": f_cond,
                        "best_offer_only": f_bo,
                        "tag": f_tag.strip() or "General",
                        "notes": f_notes
                    }
                    st.session_state.replens.append(new_item)
                    save_replens(st.session_state.replens)
                    st.success(f"Added {f_title} to live monitoring!")
                    st.rerun()

    if st.session_state.replens:
        df = pd.DataFrame(st.session_state.replens)
        st.dataframe(
            df[["tag", "asin", "title", "target_price", "amazon_price", "condition", "notes"]],
            column_config={
                "tag": "Tag",
                "asin": "ASIN",
                "title": "Title / Keywords",
                "target_price": st.column_config.NumberColumn("Target Buy ($)", format="$%.2f"),
                "amazon_price": st.column_config.NumberColumn("Amazon Sell ($)", format="$%.2f"),
                "condition": "Condition",
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
