from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt

# Load environment variables from .env
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# Define HTML template for Web Speech API recognition
HtmlCode = '''<!DOCTYPE html>
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

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
            }
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace language setting dynamically
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Ensure Data folder exists and write Voice.html safely
current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "Data")
os.makedirs(data_dir, exist_ok=True)
html_file_path = os.path.join(data_dir, "Voice.html")

with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

Link = f"file://{os.path.abspath(html_file_path)}"

# Configure Chrome Headless Options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--allow-file-access-from-files")

# Initialize Selenium Driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    """Write assistant status to file safely."""
    try:
        with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception as e:
        pass

def QueryModifier(Query):
    """Format prompt with appropriate punctuation and capitalization."""
    new_query = Query.lower().strip()
    query_words = new_query.split()
    if not query_words:
        return ""

    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Add question mark or period logically
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

            time.sleep(0.1)  # Prevents CPU overload in infinite loop
        except Exception:
            pass

if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            if Text:
                print(f"Recognized: {Text}")
    except KeyboardInterrupt:
        print("\nStopping Speech Recognition...")
    finally:
        driver.quit()