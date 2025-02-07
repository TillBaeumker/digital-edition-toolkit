import streamlit as st
from playwright.sync_api import sync_playwright

def check_search_playwright(url):
    """Prüft mit Playwright, ob eine Website eine Suchfunktion hat und gibt das Ergebnis zurück."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)
        
        # Prüfen, ob ein Suchfeld existiert
        search_field = page.query_selector('input[type="search"], input[name*="search"], input[placeholder*="Suche"]')

        browser.close()

        return search_field is not None  # Gibt True zurück, falls ein Suchfeld existiert

# **Streamlit UI**
st.title("🔍 Playwright-Suchprüfung für digitale Editionen")
url = st.text_input("🌍 Website-URL eingeben", "")

if st.button("🔍 Suche analysieren"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
    else:
        st.info(f"🔄 Überprüfe {url} mit Playwright...")
        try:
            has_search = check_search_playwright(url)
            if has_search:
                st.success("✅ Suchfeld gefunden!")
            else:
                st.error("❌ Kein Suchfeld gefunden!")
        except Exception as e:
            st.error(f"⚠️ Fehler bei der Analyse: {str(e)}")
