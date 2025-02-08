import streamlit as st
import requests
from autoscraper import AutoScraper
from bs4 import BeautifulSoup

st.title("🔍 AutoScraper Evaluierung digitaler Editionen")

# 📝 Eingabefeld für die URL der digitalen Edition
url = st.text_input("🔗 URL der digitalen Edition:")

# 📌 Kriterien aus dem IDE-Katalog
st.subheader("📌 Wähle die zu überprüfenden Kriterien:")
check_search = st.checkbox("🔎 Suchfunktion")
check_metadata = st.checkbox("📄 Metadaten (Dublin Core, TEI-Header)")
check_citation = st.checkbox("📌 Zitierfähigkeit (DOI, Permalink)")
check_access = st.checkbox("🗝️ Offener Zugang")
check_api = st.checkbox("⚙️ Technische Schnittstellen (OAI-PMH, REST)")
check_browsing = st.checkbox("📂 Browsing-Funktion")
check_images = st.checkbox("🖼️ Bildanzeige & Zoom-Funktion")
check_links = st.checkbox("🔗 Interne/externe Verlinkungen")

# 📊 Scraper-Modell für verschiedene Kriterien
scraper = AutoScraper()

# 🏗️ Trainingsdaten für AutoScraper definieren
search_example = ["Suchfeld gefunden"]
metadata_example = ["Metadaten vorhanden"]
citation_example = ["DOI gefunden"]
access_example = ["Frei zugänglich"]
api_example = ["API vorhanden"]
browsing_example = ["Browsing-Funktion gefunden"]
images_example = ["Zoom-Funktion vorhanden"]
links_example = ["50 Links gefunden"]

def analyze_page(url):
    """ Analysiert eine Seite anhand der ausgewählten Kriterien """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Fehler werfen, falls Seite nicht geladen wird
        content_type = response.headers.get("Content-Type", "").lower()
        
        # Wähle Parser basierend auf Inhaltstyp
        if "xml" in content_type:
            soup = BeautifulSoup(response.text, "xml")  # Nutzt eingebauten XML-Parser
        else:
            soup = BeautifulSoup(response.text, "html.parser")  # Nutzt eingebauten HTML-Parser

        # Ergebnisse speichern
        results = {}

        # 📌 AutoScraper trainieren & anwenden
        if check_search:
            scraper.build(response.text, search_example)
            search_results = scraper.get_result_similar(response.text)
            results["Suchfunktion"] = search_results[0] if search_results else "❌ Nicht gefunden"

        if check_metadata:
            scraper.build(response.text, metadata_example)
            metadata_results = scraper.get_result_similar(response.text)
            results["Metadaten"] = metadata_results[0] if metadata_results else "❌ Keine Metadaten"

        if check_citation:
            scraper.build(response.text, citation_example)
            citation_results = scraper.get_result_similar(response.text)
            results["Zitierfähigkeit"] = citation_results[0] if citation_results else "❌ Kein DOI"

        if check_access:
            scraper.build(response.text, access_example)
            access_results = scraper.get_result_similar(response.text)
            results["Offener Zugang"] = access_results[0] if access_results else "❌ Zugangsbeschränkt"

        if check_api:
            scraper.build(response.text, api_example)
            api_results = scraper.get_result_similar(response.text)
            results["Technische Schnittstellen"] = api_results[0] if api_results else "❌ Keine API gefunden"

        if check_browsing:
            scraper.build(response.text, browsing_example)
            browsing_results = scraper.get_result_similar(response.text)
            results["Browsing-Funktion"] = browsing_results[0] if browsing_results else "❌ Keine Navigation"

        if check_images:
            scraper.build(response.text, images_example)
            images_results = scraper.get_result_similar(response.text)
            results["Bildanzeige & Zoom"] = images_results[0] if images_results else "❌ Kein Zoom"

        if check_links:
            scraper.build(response.text, links_example)
            links_results = scraper.get_result_similar(response.text)
            results["Verlinkungen"] = links_results[0] if links_results else "❌ Keine Links gefunden"

        return results

    except requests.exceptions.RequestException as e:
        return {"Fehler": f"❌ Fehler beim Laden der Seite: {e}"}

if st.button("🔍 Edition analysieren"):
    if not url:
        st.error("Bitte eine URL eingeben!")
    else:
        results = analyze_page(url)

        # 📊 Ergebnisse ausgeben
        st.subheader("📊 Ergebnisse der Analyse")
        for key, value in results.items():
            st.write(f"✅ {key}: {value}")
