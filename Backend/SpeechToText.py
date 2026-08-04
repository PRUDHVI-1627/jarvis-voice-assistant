from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import atexit
import mtranslate as mt

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")
TEMP_DIR = os.path.join(BASE_DIR, "Frontend", "Files")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Load environment variables
env_vars = dotenv_values(os.path.join(BASE_DIR, ".env"))
InputLanguage = env_vars.get("InputLanguage", "en")

# Define HTML template for Web Speech API recognition
HtmlCode = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '{InputLanguage}';
            recognition.continuous = true;

            recognition.onresult = function(event) {{
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            }};

            recognition.onend = function() {{
                recognition.start();
            }};
            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
            output.innerHTML = "";
        }}
    </script>
</body>
</html>'''

# Write HTML file safely
html_file_path = os.path.join(DATA_DIR, "Voice.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

Link = f"file://{os.path.abspath(html_file_path)}"

# Configure Chrome Headless Options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--allow-file-access-from-files")

# Initialize Selenium Driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Ensure driver quits cleanly when script or GUI exits
def close_driver():
    try:
        driver.quit()
    except Exception:
        pass

atexit.register(close_driver)


def SetAssistantStatus(Status):
    """Write assistant status to file safely."""
    try:
        with open(os.path.join(TEMP_DIR, 'Status.data'), "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception:
        pass


def QueryModifier(Query):
    """Format prompt with appropriate punctuation and capitalization."""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    if not query_words:
        return ""

    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(new_query.startswith(word) for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()


def UniversalTranslator(Text):
    """Translate non-English audio to English."""
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()


def SpeechRecognition():
    """Captures audio stream output from headless Chrome session."""
    driver.get(Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text

            if Text:
                driver.find_element(By.ID, "end").click()

                if "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating ...")
                    return QueryModifier(UniversalTranslator(Text))

            time.sleep(0.1)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        while True:
            recognized_text = SpeechRecognition()
            if recognized_text:
                print(f"Recognized: {recognized_text}")
    except KeyboardInterrupt:
        print("\nStopping Speech Recognition...")
    finally:
        close_driver()