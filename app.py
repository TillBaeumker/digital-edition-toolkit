import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError
import openai
import os
from dotenv import load_dotenv
import validators

# Sicherstellen, dass Playwright-Browser installiert sind
os.system("playwright install")
os.system("playwright install-deps")

# Lade Umgebungsvariablen
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", None))

# Prüfe, ob der OpenAI API-Key vorhanden ist
if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API-Key fehlt! Bitte stelle sicher, dass ein API-Key in `.env` oder `st.secrets` hinterlegt ist.")
    st.stop()

openai.api_key = OPENAI_API_KEY

# Titel der App
st.title("🔍 Digital Edition Tester")
st.write("Gib eine Website-URL ein und beschreibe, was getestet werden soll.")

# Eingabefelder
url = st.text_input("🌍 Website-URL", "")
test_prompt = st.text_area("📝 Was soll getestet werden?", "")

# Button zum Starten des Tests
if st.button("🚀 Test starten"):
    if not url or not test_prompt:
        st.warning("⚠️ Bitte eine URL und eine Testbeschreibung eingeben.")
        st.stop()

    if not validators.url(url):
        st.error("🚫 Ungültige URL! Bitte eine gültige Webadresse eingeben.")
        st.stop()

    st.info(f"🔄 Starte Tests für {url} ...")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)  # Headless für Cloud
            page = browser.new_page()
            page.goto(url, timeout=10000)  # Timeout für langsam ladende Seiten

            # OpenAI generiert eine Testanweisung basierend auf der Testbeschreibung
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Du bist ein Web-Testing-Assistent."},
                    {"role": "user", "content": f"Teste diese Website: {url}. {test_prompt}"}
                ],
                max_tokens=150
            )
            test_instruction = response["choices"][0]["message"]["content"]
            st.subheader("🔎 Generierte Testanweisung:")
            st.write(test_instruction)

            # Sammle alle Links auf der Seite
            links = page.locator("a").all()
            link_list = [link.get_attribute("href") for link in links if link.get_attribute("href")]
            st.subheader(f"🔗 Gefundene Links ({len(link_list)}):")
            st.write(link_list[:10])  # Zeigt die ersten 10 Links zur Übersicht

            browser.close()
            st.success("✅ Test abgeschlossen!")

        except TimeoutError:
            st.error("⏳ Fehler: Die Website hat zu lange zum Laden gebraucht.")
        except Exception as e:
            st.error(f"⚠️ Unerwarteter Fehler: {str(e)}")
