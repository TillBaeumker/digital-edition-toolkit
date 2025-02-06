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
st.write("🔍 Wähle die gewünschten Tests aus:")

# **Checkboxen für Tests**
check_links = st.checkbox("🔗 Funktionalität der Links prüfen")
check_images = st.checkbox("🖼️ Bilder geladen?")
check_search = st.checkbox("🔍 Funktioniert die Suche?")
check_login = st.checkbox("🔑 Login-Funktion testen?")
check_api = st.checkbox("🖥️ API erreichbar?")
check_metadata = st.checkbox("📄 Metadaten korrekt?")

# **Button zum Starten des Tests**
if st.button("🚀 Test starten"):
    if not url:
        st.warning("⚠️ Bitte eine URL eingeben.")
        st.stop()
    if not validators.url(url):
        st.error("🚫 Ungültige URL! Bitte eine gültige Webadresse eingeben.")
        st.stop()

    st.info(f"🔄 Starte Tests für {url} ...")

    test_code = f"""
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("{url}", timeout=15000, wait_until="domcontentloaded")
        yield page
        page.close()
        browser.close()
    """

    if check_links:
        test_code += """
def test_check_links(page):
    links = page.locator("a").all()
    assert len(links) > 0, "Es wurden keine Links gefunden."
    """

    if check_images:
        test_code += """
def test_check_images(page):
    images = page.locator("img").all()
    assert len(images) > 0, "Es wurden keine Bilder gefunden."
    """

    if check_search:
        test_code += """
def test_check_search(page):
    search_box = page.locator("input[type='search'], input[name='q']")
    assert search_box.count() > 0, "Keine Suchleiste gefunden."
    """

    if check_login:
        test_code += """
def test_check_login(page):
    login_button = page.locator("button:has-text('Login'), input[type='submit']")
    assert login_button.count() > 0, "Kein Login-Button gefunden."
    """

    if check_api:
        test_code += """
def test_check_api(page):
    response = page.evaluate("() => fetch('/api').then(res => res.status)")
    assert response == 200, "API nicht erreichbar oder Fehlercode zurückgegeben."
    """

    if check_metadata:
        test_code += """
def test_check_metadata(page):
    meta_tags = page.locator("meta").all()
    assert len(meta_tags) > 0, "Keine Metadaten gefunden."
    """

    # **Generierten Code speichern**
    test_file = "test_generated.py"
    with open(test_file, "w") as f:
        f.write(test_code)

    st.subheader("📌 Generierter Playwright + Pytest Code:")
    st.code(test_code, language="python")

    # **⚡ Pytest automatisch ausführen**
    try:
        result = subprocess.run(["pytest", test_file, "--disable-warnings"], capture_output=True, text=True)
        st.subheader("📊 Testergebnisse:")
        st.text(result.stdout)  # Zeigt die Ergebnisse an

        # **KI-Zusammenfassung der Ergebnisse**
        summary_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"Erstelle eine verständliche, zusammenfassende Bewertung basierend auf diesen Testergebnissen:\n\n{result.stdout}"
            }],
            max_tokens=300
        )
        summary = summary_response.choices[0].message.content.strip()
        st.subheader("📄 Zusammenfassung der Ergebnisse:")
        st.write(summary)

        if result.returncode == 0:
            st.success("✅ Alle Tests erfolgreich bestanden!")
        else:
            st.error("❌ Einige Tests sind fehlgeschlagen. Siehe Logs oben.")

    except Exception as e:
        st.error(f"⚠️ Fehler bei der Testausführung: {str(e)}")

    st.success("✅ Test abgeschlossen!")
