import requests
from bs4 import BeautifulSoup
import streamlit as st

def check_search_function(url):
    """Prüft, ob eine digitale Edition eine Suchfunktion hat."""
    
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Fehler: Konnte die Seite nicht abrufen (Status {response.status_code})"
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    search_score = 0  # Basisbewertung

    results = {
        "Suchfeld gefunden": False,
        "Suchformular gefunden": False,
        "Suchlink gefunden": False,
        "Gesamtbewertung": 0
    }

    # **1️⃣ Direkte Eingabefelder für die Suche prüfen**
    search_fields = soup.find_all("input", {"type": ["text", "search"]})
    if search_fields:
        results["Suchfeld gefunden"] = True
        search_score += 2  # Wert für ein vorhandenes Suchfeld

    # **2️⃣ Suchformular (`<form>`) prüfen**
    search_forms = soup.find_all("form")
    for form in search_forms:
        if "search" in str(form).lower():
            results["Suchformular gefunden"] = True
            search_score += 2  # Wert für ein Formular

    # **3️⃣ Suchlinks (`<a href="search.html">`) prüfen**
    search_links = soup.find_all("a", href=True)
    for link in search_links:
        if "search" in link["href"].lower():
            results["Suchlink gefunden"] = True
            search_score += 1  # Geringerer Wert, weil es nur zu einer Suchseite führt

    results["Gesamtbewertung"] = search_score

    return results

# **Streamlit UI**
st.title("🔍 Analyse der Suchfunktion einer digitalen Edition")
url = st.text_input("🌍 Website-URL eingeben", "")

if st.button("🔍 Analyse starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
    else:
        search_results = check_search_function(url)
        st.subheader("📌 Suchfunktionsanalyse:")
        st.json(search_results)
