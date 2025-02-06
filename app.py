import os
import streamlit as st
import openai
import validators
import subprocess
from playwright.sync_api import sync_playwright

# **Erforderliche Abhängigkeiten prüfen und installieren**
if not os.path.exists("/home/adminuser/.cache/ms-playwright"):
    os.system("playwright install")
    os.system("playwright install-deps")

# **OpenAI API-Schlüssel aus Streamlit Secrets laden**
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ OpenAI API-Key fehlt! Bitte in `st.secrets.toml` hinterlegen.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# **📌 Streamlit UI**
st.title("🖥️ KI-gesteuerte End-to-End-Tests mit Playwright & Pytest")
st.write("Gib eine Website-URL ein und wähle die zu testenden Kriterien:")

# **Eingabefelder**
url = st.text_input("🌍 Website-URL", "")
test_prompt = st.text_area("📝 Beschreibung der gewünschten Tests (optional)", "")

# **Checkboxen für spezifische Tests**
st.subheader("🔍 Welche Aspekte sollen getestet werden?")
test_options = {
    "check_links": st.checkbox("🔗 Links prüfen"),
    "check_images": st.checkbox("🖼️ Bildanzeige prüfen"),
    "check_search": st.checkbox("🔍 Suchfunktion testen"),
    "check_login": st.checkbox("🔑 Login testen"),
    "check_api": st.checkbox("🖥️ API-Verfügbarkeit testen"),
    "check_metadata": st.checkbox("📄 Metadaten überprüfen"),
}

# **Funktion zur Code-Bereinigung**
def clean_generated_code(code):
    """Entfernt Markdown-Codeblöcke und gibt nur den reinen Python-Code zurück."""
    return code.replace("```python", "").replace("```", "").strip()

# **Button zum Starten des Tests**
if st.button("🚀 Test starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
        st.stop()
    if not validators.url(url):
        st.error("🚫 Ungültige URL! Bitte eine gültige Webadresse eingeben.")
        st.stop()

    st.info(f"🔄 Starte Tests für {url} ...")

    selected_tests = [key for key, value in test_options.items() if value]
    if not selected_tests:
        st.warning("⚠️ Bitte mindestens einen Test auswählen.")
        st.stop()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000, wait_until="domcontentloaded")

        # **GPT-4 generiert Playwright-Testcode für pytest**
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"Schreibe einen vollständigen Playwright-Pytest-Test für folgende Anforderungen: {test_prompt}. "
                           f"Die Tests sollen sich auf folgende Punkte beziehen: {', '.join(selected_tests)}. "
                           "Gib NUR den Python-Code zurück, ohne Markdown oder Kommentare."
            }],
            max_tokens=800
        )

        pytest_code = response.choices[0].message.content.strip()
        pytest_code = clean_generated_code(pytest_code)  # Entferne Markdown-Formatierung

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
            st.text(result.stdout)  # Zeigt die Testergebnisse an

            # **KI-Zusammenfassung der Ergebnisse**
            summary_response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Erstelle eine klare, prägnante Zusammenfassung der folgenden Testergebnisse:\n\n{result.stdout}"
                }],
                max_tokens=300
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
