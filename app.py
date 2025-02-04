import streamlit as st
from playwright.sync_api import sync_playwright
import openai
import os
from dotenv import load_dotenv

os.system("playwright install")



# Lade API-Keys aus Streamlit Secrets oder .env-Datei
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

st.title("🔍 Digital Edition Tester")
st.write("Gib eine Website-URL und eine Testbeschreibung ein")

# Eingabefelder für URL und Testbeschreibung
url = st.text_input("🌍 Website URL", "")
test_prompt = st.text_area("📝 Was soll getestet werden?", "")

if st.button("🚀 Test starten"):
    if url and test_prompt:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # OpenAI generiert eine Testanweisung
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Du bist ein Test-Assistent für Web-Automation."},
                    {"role": "user", "content": f"Teste diese Website: {url}. {test_prompt}"}
                ],
                max_tokens=100
            )
            test_instruction = response["choices"][0]["message"]["content"]
            st.write("🔎 Generierte Testanweisung:", test_instruction)

            # Beispiel: Alle Links auf der Seite extrahieren
            links = page.locator("a").all()
            link_list = [link.get_attribute("href") for link in links if link.get_attribute("href")]
            st.write(f"🔗 Gefundene Links: {len(link_list)}")
            st.write(link_list[:5])  # Zeigt die ersten 5 Links

            browser.close()
            st.success("✅ Test abgeschlossen!")

    else:
        st.warning("⚠️ Bitte URL und Testbeschreibung eingeben.")
