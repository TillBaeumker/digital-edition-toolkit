import os
import streamlit as st
import openai
import validators
import subprocess
from playwright.sync_api import sync_playwright

# **Erforderliche Abhängigkeiten installieren**
os.system("playwright install")
os.system("playwright install-deps")

# **OpenAI API-Schlüssel aus Streamlit Secrets laden**
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API-Key fehlt! Bitte in `st.secrets.toml` hinterlegen.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# **📌 Streamlit UI**
st.title("🖥️ AI-gesteuerte End-to-End-Tests mit Playwright & Pytest")
st.write("Gib eine Testanweisung in natürlicher Sprache ein:")

# **Eingabefelder**
url = st.text_input("🌍 Website-URL", "")
test_prompt = st.text_area("📝 Was soll getestet werden?", "")

# **Button zum Starten des Tests**
if st.button("🚀 Test starten"):
    if not url or not test_prompt:
        st.warning("⚠️ Bitte eine URL und eine Testbeschreibung eingeben.")
        st.stop()

    if not validators.url(url):
        st.error("🚫 Ungültige URL! Bitte eine gültige Webadresse eingeben.")
        st.stop()

    st.info(f"🔄 Starte Tests für {url} ...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000, wait_until="domcontentloaded")

        # **GPT-4 generiert Playwright-Testcode für pytest**
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"Schreibe ein vollständiges Playwright-Pytest-Testskript für folgende Aufgabe: {test_prompt}. "
                           "Gib nur reinen ausführbaren Python-Code zurück, ohne Erklärungen oder Kommentare."
            }],
            max_tokens=500
        )

        pytest_code = response.choices[0].message.content.strip()

        # **Überprüfung auf gültigen Code**
        if "import" not in pytest_code or "def test_" not in pytest_code:
            st.error("⚠️ OpenAI hat keinen gültigen Python-Testcode generiert. Versuche es mit einer präziseren Anweisung.")
            st.stop()

        # **Generierten Code speichern**
        test_file = "test_generated.py"
        with open(test_file, "w") as f:
            f.write(pytest_code)

        st.subheader("📌 Generierter Playwright + Pytest Code:")
        st.code(pytest_code, language="python")

        # **⚡ Pytest automatisch ausführen**
        try:
            result = subprocess.run(["pytest", test_file, "--disable-warnings"], capture_output=True, text=True)
            st.subheader("📊 Testergebnisse:")
            st.text(result.stdout)  # Zeigt die Ergebnisse an

            if result.returncode == 0:
                st.success("✅ Alle Tests erfolgreich bestanden!")
            else:
                st.error("❌ Einige Tests sind fehlgeschlagen. Siehe Logs oben.")

        except Exception as e:
            st.error(f"⚠️ Fehler bei der Testausführung: {str(e)}")

        browser.close()
        st.success("✅ Test abgeschlossen!")
