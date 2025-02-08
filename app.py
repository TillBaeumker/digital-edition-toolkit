import streamlit as st
from playwright.sync_api import sync_playwright

def check_search_playwright(url):
    """Prüft mit Playwright, ob eine Website eine Suchfunktion hat."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)

        search_field = page.query_selector('input[type="search"], input[name*="search"], input[placeholder*="Suche"]')

        browser.close()
        return search_field is not None  

def check_images_playwright(url):
    """Prüft mit Playwright, ob eine Website Bilder enthält."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)

        images = page.query_selector_all("img")

        browser.close()
        return len(images)  

# **Streamlit UI**
st.title("🔍 Playwright-Analyse für digitale Editionen")

# **URL-Eingabe**
url = st.text_input("🌍 Website-URL eingeben", "")

# **Checkboxen zur Auswahl der Prüfungen**
check_search = st.checkbox("🔍 Nach Suchfunktion suchen", value=False)
check_images = st.checkbox("🖼️ Nach Bildern suchen", value=False)

# **Button zur Analyse**
if st.button("🚀 Analyse starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
    elif not check_search and not check_images:
        st.warning("⚠️ Bitte mindestens eine Option auswählen.")
    else:
        st.info(f"🔄 Überprüfe {url} mit Playwright...")

        try:
            # **Ergebnisse initialisieren**
            results = {}

            # **Suchfunktion prüfen**
            if check_search:
                has_search = check_search_playwright(url)
                results["Suchfunktion"] = "✅ Vorhanden" if has_search else "❌ Nicht gefunden"

            # **Bilder prüfen**
            if check_images:
                image_count = check_images_playwright(url)
                results["Bilder"] = f"🖼️ {image_count} Bild(er) gefunden" if image_count > 0 else "❌ Keine Bilder gefunden"

            # **Ergebnisse anzeigen**
            st.success("✅ Analyse abgeschlossen!")
            for key, value in results.items():
                st.write(f"**{key}:** {value}")

        except Exception as e:
            st.error(f"⚠️ Fehler bei der Analyse: {str(e)}")
