import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def analyze_search_function(url):
    """Untersucht die Suchfunktionen auf einer Webseite."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        
        # HTML der Seite abrufen
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Alle Eingabefelder suchen
        search_fields = soup.find_all("input", {"type": ["text", "search"]})
        
        results = []
        for field in search_fields:
            name = field.get("name", "Unbekannt")
            placeholder = field.get("placeholder", "Kein Placeholder")
            autocomplete = field.get("autocomplete", "Nicht angegeben")
            
            results.append({
                "Name": name,
                "Placeholder": placeholder,
                "Autocomplete": autocomplete
            })
        
        browser.close()
        
        return results

# **Streamlit UI**
st.title("🔍 Website-Suchfunktion analysieren")
url = st.text_input("🌍 Website-URL eingeben", "")

if st.button("🔍 Suche analysieren"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
    else:
        search_results = analyze_search_function(url)
        if search_results:
            st.subheader("📌 Gefundene Suchfelder:")
            for result in search_results:
                st.write(f"- **Name:** {result['Name']}, **Placeholder:** {result['Placeholder']}, **Autocomplete:** {result['Autocomplete']}")
        else:
            st.write("❌ Keine Suchfelder gefunden.")
