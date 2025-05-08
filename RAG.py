import os
import pandas as pd
from scraper import scrape_airline_pages
from auditor import audit_features
import streamlit as st


features = [
    "Airport parking online booking",
    "Baggage Allowance Upgrades",
    "Baggage collection (home-to-airport)",
    "Baggage wrapping and protection services",
    "BNPL",
    "buy tickets with apple pay/google pay",
    "Carbon offset package",
    "Charter services",
    "Corporate Offerings",
    "Crypto Payment",
    "Dynamic Pricing",
    "Flight bundles/packages",
    "Flight Changes",
    "Flight classes",
    "gift cards",
    "Group bookings",
    "Holiday Packages",
    "Home Check In",
    "Lounges",
    "Loyalty programmes",
    "Meet and assist services",
    "Multi-currency payment options",
    "Online Check in",
    "Pet handling and travel services",
    "Pre-Order Inflight Ancilliaries",
    "Pre-Order Inflight Meals",
    "Promotions",
    "Seat selection & upgrades",
    "Special cargo upgrades",
    "Subscription",
    "Travel Insurance",
    "Airport transfers",
    "Attraction tickets & bookings (theme parks, museums, theaters)",
    "Baggage Delivery (airport to home)",
    "Car hire & rental services",
    "E-hailing Partnership",
    "e-Sim",
    "Event ticketing (concerts, sports events, festivals)",
    "Fast-track",
    "Grocery delivery",
    "Helicopter transfer",
    "Home Delivery of duty free items",
    "Hotel and accommodation bookings",
    "Public transportation passes (city metro/train/bus)",
    "Restaurant reservations & dining experiences",
    "Tours and Activities",
    "24/7 support",
    "card partnerships",
    "Chatbot",
    "Fintech Solutions",
    "jet lag solutions",
    "Pay with points",
    "POS",
    "Social Features(eg. Community)",
    "Accessible travel",
    "Baggage delay insurance",
    "Biometric check-in/boarding",
    "Buy-on-board",
    "Crew Sales Incentive programme",
    "Customer segment specific platforms (eg. Ikhlas)",
    "Digital duty-free retail platforms",
    "Digital health credentials",
    "Family services",
    "IFE (In-flight Entertainment) systems",
    "Inflight Wi-Fi access (free or paid)",
    "IoT solutions for cabin management (smart seats, personalized lighting)",
    "Language translation services",
    "Live Tracking",
    "lottery tickets",
    "Mobile crew management solutions (crew tablets, real-time passenger data)",
    "order 2 seat",
    "Passenger-facing apps",
    "Personalized marketing",
    "Pre-Order Duty Free",
    "Premium dining experiences (e.g., chef-curated menus, wine pairing)",
    "Special dietary meals",
    "Store pickup",
    "VR and AR experiences",
    "Wellness and mindfulness programs (nutrition planner, guided meditation, relaxation content)"
]

st.set_page_config(page_title="Airline Feature Auditor", layout="wide")
st.title("✈️ Airline Ancillary Feature Auditor")

st.markdown("This tool scrapes an airline's site and uses AI to detect if 80+ ancillary services are offered.")

# 🔧 UI Inputs
base_url = st.text_input("Enter airline homepage URL", "https://www.easyjet.com")
keywords = st.text_input("Keywords to help find relevant links (comma-separated)", "book,check,lounge,extras,services").split(",")
max_links = st.slider("Max Pages to Scrape", min_value=5, max_value=50, value=20)
depth = st.slider("Link Depth (click levels from homepage)", min_value=1, max_value=3, value=2)

# 🧠 Run Audit
if st.button("Run Audit"):
    with st.spinner("Scraping and analyzing the website..."):
        try:
            docs, labels = scrape_airline_pages(base_url, keywords, max_links=max_links, depth=depth)
            st.success(f"✅ Scraped {len(docs)} pages.")

            audit = audit_features(docs, features, labels)
            df = pd.DataFrame(audit)

            df["Final Decision"] = df["Final Decision"].astype(str)

            found_count = sum(df["Final Decision"] == "True")
            not_found_count = sum(df["Final Decision"] == "False")
            unclear_count = sum(df["Final Decision"] == "Unclear")
            total = len(df)

            st.subheader("📈 Summary Dashboard")

            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Confirmed Features", found_count)
            col2.metric("❌ Missing Features", not_found_count)
            col3.metric("🤔 Unclear", unclear_count)

            st.subheader("Feature Detection Breakdown")
            chart_data = pd.DataFrame({
                "Status": ["Found", "Not Found", "Unclear"],
                "Count": [found_count, not_found_count, unclear_count]
            })
            st.bar_chart(chart_data.set_index("Status"))

            st.subheader("📄 Detailed Results")
            st.dataframe(df, use_container_width=True)

            # CSV download
            st.download_button("📥 Download Results as CSV", data=df.to_csv(index=False),
                            file_name="airline_audit_results.csv", mime="text/csv")


        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")