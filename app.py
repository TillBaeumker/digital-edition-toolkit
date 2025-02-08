import streamlit as st
from playwright.sync_api import sync_playwright

# Funktion zum Laden der Seite mit Playwright
def load_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=15000)  # 15 Sekunden Timeout
            return page
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Seite: {e}")
            return None
        finally:
            browser.close()

# Prüft, ob eine Suchfunktion vorhanden ist
def check_search_function(page):
    search_field = page.query_selector('input[type="search"], input[name*="search"], input[placeholder*="Suche"]')
    return search_field is not None

# Prüft, ob Bilder vorhanden sind
def check_images(page):
    images = page.query_selector_all("img")
    return len(images)

# Prüft, ob Metadaten (TEI, Dublin Core) vorhanden sind
def check_metadata(page):
    tei_meta = page.query_selector("teiHeader, metadata, meta[name*='DC']")
    return tei_meta is not None

# Prüft, wie viele Links auf der Seite vorhanden sind
def check_links(page):
    links = page.query_selector_all("a")
    return len(links)

# **Streamlit UI**
st.title("🔍 Playwright-Analyse für digitale Editionen")

# **URL-Eingabe**
url = st.text_input("🌍 Website-URL eingeben", "")

# **Checkboxen zur Auswahl der Prüfungen**
check_search = st.checkbox("🔍 Nach Suchfunktion suchen", value=False)
check_images = st.checkbox("🖼️ Nach Bildern suchen", value=False)
check_metadata = st.checkbox("📄 Nach Metadaten (TEI, Dublin Core) suchen", value=False)
check_links = st.checkbox("🔗 Anzahl der Links prüfen", value=False)

# **Button zur Analyse**
if st.button("🚀 Analyse starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
    elif not any([check_search, check_images, check_metadata, check_links]):
        st.warning("⚠️ Bitte mindestens eine Option auswählen.")
    else:
        st.info(f"🔄 Lade {url} mit Playwright...")

        # **Lade die Seite mit Playwright**
        page = load_page(url)
        if page is None:
            st.error("⚠️ Fehler: Konnte die Seite nicht laden.")
        else:
            results = {}

            # **Suchfunktion prüfen**
            if check_search:
                has_search = check_search_function(page)
                results["Suchfunktion"] = "✅ Vorhanden" if has_search else "❌ Nicht gefunden"

            # **Bilder prüfen**
            if check_images:
                image_count = check_images(page)
                results["Bilder"] = f"🖼️ {image_count} Bild(er) gefunden" if image_count > 0 else "❌ Keine Bilder gefunden"

            # **Metadaten prüfen**
            if check_metadata:
                has_metadata = check_metadata(page)
                results["Metadaten"] = "✅ Vorhanden" if has_metadata else "❌ Keine Metadaten gefunden"

            # **Anzahl der Links prüfen**
            if check_links:
                link_count = check_links(page)
                results["Verlinkungen"] = f"🔗 {link_count} Link(s) gefunden"

            # **Ergebnisse anzeigen**
            st.success("✅ Analyse abgeschlossen!")
            for key, value in results.items():
                st.write(f"**{key}:** {value}")
