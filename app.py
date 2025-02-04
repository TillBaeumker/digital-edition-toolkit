import streamlit as st
from playwright.sync_api import sync_playwright
from auto_playwright import auto
import os
from dotenv import load_dotenv

# Lade API-Keys aus GitHub Secrets oder .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.title("🔍 Digital Edition Tester")
st.write("Gib eine Website-URL und eine Testbeschreibung ein")

url = st.text_input("🌍 Website URL", "")
test_prompt = st.text_area("📝 Was soll getestet werden?", "")

if st.button("🚀 Test starten"):
    if url and test_prompt:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # Auto Playwright Test
            result = auto(test_prompt, {"page": page})

            # Ergebnis anzeigen
            st.success("✅ Test abgeschlossen!")
            st.write(result)

            browser.close()
    else:
        st.warning("⚠️ Bitte URL und Testbeschreibung eingeben.")
