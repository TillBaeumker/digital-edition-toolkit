import streamlit as st
import httpx  # Besser als requests für Scraping
from autoscraper import AutoScraper
from bs4 import BeautifulSoup

st.title("🔍 AutoScraper Evaluierung digitaler Editionen")

# Eingabe der URL durch den Nutzer
url = st.text_input("🔗 URL der digitalen Edition:")

# Kriterien aus dem IDE-Katalog
st.subheader("📌 Wähle die zu überprüfenden Kriterien:")
criteria_checkboxes = {
    "Suchfunktion": st.checkbox("🔎 Suchfunktion"),
    "Metadaten": st.checkbox("📄 Metadaten (Dublin Core, TEI-Header)"),
    "Zitierfähigkeit": st.checkbox("📌 Zitierfähigkeit (DOI, Permalink)"),
    "Offener Zugang": st.checkbox("🗝️ Offener Zugang"),
    "Technische Schnittstellen": st.checkbox("⚙️ Technische Schnittstellen (OAI-PMH, REST)"),
    "Browsing-Funktion": st.checkbox("📂 Browsing-Funktion"),
    "Bildanzeige & Zoom": st.checkbox("🖼️ Bildanzeige & Zoom-Funktion"),
    "Verlinkungen": st.checkbox("🔗 Interne/externe Verlinkungen")
}

# Scraper-Modell für verschiedene Kriterien
scraper = AutoScraper()

# Trainingsdaten für AutoScraper definieren
training_data = {
    "Suchfunktion": ["Suchfeld gefunden"],
    "Metadaten": ["Metadaten vorhanden"],
    "Zitierfähigkeit": ["DOI gefunden"],
    "Offener Zugang": ["Frei zugänglich"],
    "Technische Schnittstellen": ["API vorhanden"],
    "Browsing-Funktion": ["Browsing-Funktion gefunden"],
    "Bildanzeige & Zoom": ["Zoom-Funktion vorhanden"],
    "Verlinkungen": ["50 Links gefunden"]
}

def fetch_website(url):
    """ Holt den HTML-Inhalt der Webseite mit httpx """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            return response.text, response.headers.get("Content-Type", "").lower()
    except httpx.RequestError as e:
        return None, f"❌ Netzwerkfehler: {e}"
    except httpx.HTTPStatusError as e:
        return None, f"❌ Fehler {e.response.status_code}: {e.response.text}"

if st.button("🔍 Edition analysieren"):
    if not url:
        st.error("❌ Fehler: Bitte eine gültige URL eingeben!")
    elif not url.startswith("http"):
        st.error("❌ Fehler: Die URL muss mit 'http://' oder 'https://' beginnen.")
    else:
        html_content, content_type = fetch_website(url)

        if not html_content:
            st.error(content_type)  # Gibt die Netzwerk-Fehlermeldung aus
        else:
            # Bestimmen, ob HTML oder XML
            if "xml" in content_type:
                soup = BeautifulSoup(html_content, "xml")  # XML-Parser
            else:
                soup = BeautifulSoup(html_content, "html.parser")  # HTML-Parser

            # Ergebnisse speichern
            results = {}

            # AutoScraper einmal trainieren & für alle Kriterien nutzen
            for criterion, example in training_data.items():
                if criteria_checkboxes.get(criterion, False):  # Prüfen, ob die Checkbox aktiviert wurde
                    scraper.build(html_content, example)
                    scraper_results = scraper.get_result_similar(html_content)
                    results[criterion] = scraper_results[0] if scraper_results else "❌ Nicht gefunden"

            # Ergebnisse ausgeben
            st.subheader("📊 Ergebnisse der Analyse")
            for key, value in results.items():
                st.write(f"✅ {key}: {value}")
