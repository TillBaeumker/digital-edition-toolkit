import os
import streamlit as st
import openai
import validators
import subprocess
from playwright.sync_api import sync_playwright

# **Erforderliche Abhängigkeiten installieren**
os.system("playwright install")
os.system("playwright install-deps")

# **OpenAI API-Schlüssel**
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API-Key fehlt! Bitte in `st.secrets.toml` hinterlegen.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# **📌 Streamlit UI**
st.title("🖥️ KI-gestützte End-to-End-Tests mit Playwright & Pytest")
st.write("Gib eine Website-URL ein und wähle, was getestet werden soll:")

# **Eingabefelder**
url = st.text_input("🌍 Website-URL", "")
test_prompt = st.text_area("📝 Beschreibung der gewünschten Tests (optional)", "")

# **Checkboxen für spezifische Tests**
st.subheader("🔍 Welche Aspekte sollen getestet werden?")
test_options = {
    "check_links": st.checkbox("🔗 Funktionalität der Links"),
    "check_images": st.checkbox("🖼️ Sind Bilder sichtbar?"),
    "check_api": st.checkbox("🖥️ Funktionieren API-Aufrufe?"),
    "check_forms": st.checkbox("📝 Funktionieren Formulareingaben?"),
    "check_metadata": st.checkbox("📄 Sind Metadaten vorhanden?"),
}

# **Code-Cleanup-Funktion**
def clean_generated_code(code):
    """Entfernt Markdown-Codeblöcke und gibt reinen Python-Code zurück."""
    if code.startswith("```python"):
        code = code.replace("```python", "").strip()
    if code.endswith("```"):
        code = code.replace("```", "").strip()
    return code

# **Button zum Starten der Tests**
if st.button("🚀 Test starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
        st.stop()
    if not validators.url(url):
        st.error("🚫 Ungültige URL! Bitte eine gültige Webadresse eingeben.")
        st.stop()

    selected_tests = [key for key, value in test_options.items() if value]
    if not selected_tests:
        st.warning("⚠️ Bitte mindestens einen Test auswählen.")
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
                "content": f"Schreibe vollständige Playwright-Pytest-Tests für: {test_prompt}. "
                           f"Die Tests sollen sich auf folgende Punkte beziehen: {', '.join(selected_tests)}. "
                           "Gib NUR den Python-Code zurück, ohne Erklärungen oder Markdown-Formatierung."
            }],
            max_tokens=1000
        )

        pytest_code = response.choices[0].message.content.strip()
        pytest_code = clean_generated_code(pytest_code)  # Entfernt Markdown-Formatierung

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

        # **⚡ Pytest ausführen**
        try:
            result = subprocess.run(["pytest", test_file, "--disable-warnings"], capture_output=True, text=True)
            st.subheader("📊 Testergebnisse:")
            st.text(result.stdout)  # Zeigt die Testergebnisse

            # **KI-generierte Zusammenfassung der Ergebnisse**
            summary_response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Erstelle eine zusammenfassende Bewertung basierend auf diesen Testergebnissen:\n\n{result.stdout}"
                }],
                max_tokens=500
            )
            summary = summary_response.choices[0].message.content.strip()
            st.subheader("📄 Zusammenfassung der Testergebnisse:")
            st.write(summary)

            if result.returncode == 0:
                st.success("✅ Alle Tests erfolgreich bestanden!")
            else:
                st.error("❌ Einige Tests sind fehlgeschlagen. Siehe Logs oben.")

        except Exception as e:
            st.error(f"⚠️ Fehler bei der Testausführung: {str(e)}")

        browser.close()
        st.success("✅ Test abgeschlossen!")
