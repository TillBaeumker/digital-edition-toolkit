import streamlit as st
import requests
from autoscraper import AutoScraper
from bs4 import BeautifulSoup

st.title("🔍 AutoScraper Evaluierung digitaler Editionen")

# Eingabe einer URL durch den Nutzer
url = st.text_input("🔗 URL der digitalen Edition:")

if st.button("🔍 Edition analysieren"):
    if not url:
        st.error("❌ Fehler: Bitte eine gültige URL eingeben!")
    elif not url.startswith("http"):
        st.error("❌ Fehler: Die eingegebene URL ist ungültig. Stelle sicher, dass sie mit 'http://' oder 'https://' beginnt.")
    else:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Falls Seite nicht erreichbar

            # Bestimmen, ob HTML oder XML
            content_type = response.headers.get("Content-Type", "").lower()
            if "xml" in content_type:
                soup = BeautifulSoup(response.text, "xml")  # Nutzt XML-Parser
            else:
                soup = BeautifulSoup(response.text, "html.parser")  # Nutzt HTML-Parser

            # Beispiel: Titel der Seite ausgeben
            st.write(f"📌 Titel der Seite: {soup.title.string if soup.title else 'Kein Titel gefunden'}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Fehler beim Laden der Seite: {e}")
