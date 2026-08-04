# Import required libraries
from webbrowser import open as webopen  # Import web browser functionality.
from pywhatkit import search, playonyt  # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values  # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML content.
from rich import print  # Import rich for styled console output.
from groq import Groq  # Import Groq for AI chat functionalities.
import webbrowser  # Import webbrowser for opening URLs.
import subprocess  # Import subprocess for interacting with the system.
import requests  # Import requests for making HTTP requests.
import asyncio  # Import asyncio for asynchronous programming.
import os  # Import os for operating system functionalities.
import platform  # Import platform for OS identification.

# Conditional import for AppOpener (Windows fallback only)
if platform.system() == "Windows":
    try:
        from AppOpener import close, open as appopen
    except ImportError:
        pass

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.
Username = env_vars.get("Username", os.getenv("USER", "User"))  # Safe username retrieval.

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs poems, etc."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)  # Use pywhatkit's search function to perform a Google search.
    return True  # Indicate success.

# Function to open file in system default text editor (macOS / Cross-Platform)
def OpenTextFile(File):
    system_os = platform.system()
    if system_os == "Darwin":  # macOS
        subprocess.Popen(["open", File])
    elif system_os == "Windows":  # Windows
        os.startfile(File)
    else:  # Linux
        subprocess.Popen(["xdg-open", File])

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add prompt.

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Updated supported model
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        # Process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic = Topic.replace("Content ", "").replace("content ", "")
    ContentByAI = ContentWriterAI(Topic)

    # Ensure Data folder exists using cross-platform path
    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{Topic.lower().replace(' ', '')}.txt")

    # Save generated content to text file.
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenTextFile(file_path)  # Open file in default text editor.
    return True

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query)
    return True

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session()):
    system_os = platform.system()

    try:
        if system_os == "Darwin":  # macOS Native App Open
            subprocess.run(["open", "-a", app], check=True)
            return True
        elif system_os == "Windows":  # Windows App Open
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
        else:  # Linux
            subprocess.run([app], check=True)
            return True

    except Exception:
        # Fallback: Search Google and open top web link
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        
        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])

        return True

# Function to close an application.
def CloseApp(app):
    system_os = platform.system()

    if "chrome" in app.lower():
        return True

    try:
        if system_os == "Darwin":  # macOS Native Quit via AppleScript
            applescript = f'tell application "{app}" to quit'
            subprocess.run(["osascript", "-e", applescript], check=True)
            return True
        elif system_os == "Windows":  # Windows
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        else:  # Linux
            subprocess.run(["pkill", "-f", app], check=True)
            return True
    except Exception:
        return False

# Function to execute system-level commands on macOS/Windows.
def System(command):
    is_mac = platform.system() == "Darwin"

    def mute():
        if is_mac:
            os.system("osascript -e 'set volume output muted true'")

    def unmute():
        if is_mac:
            os.system("osascript -e 'set volume output muted false'")

    def volume_up():
        if is_mac:
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 10)'")

    def volume_down():
        if is_mac:
            os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) - 10)'")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True