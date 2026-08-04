from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump, JSONDecodeError  # Importing functions to read and write JSON files safely.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Updated system prompt that permits general knowledge if search snippets are limited.
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar. ***
*** Answer using the provided search results and real-time information. If search results are empty or incomplete, use your base knowledge to answer fully without mentioning empty search results. ***"""

# Cross-platform file path definition (macOS, Linux, Windows)
CHAT_LOG_PATH = "Data/ChatLog.json"

# Safely initialize or clear corrupted chat log
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)
except (FileNotFoundError, JSONDecodeError):
    messages = []
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f, indent=4)

# Function to perform Google Search (Reduced to 3 results for speed)
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=3))
        
        if not results:
            return f"No search results returned for '{query}'."

        Answer = f"The search results for '{query}' are:\n[start]\n"
        for i in results:
            title = getattr(i, 'title', 'No Title')
            description = getattr(i, 'description', 'No Description')
            url = getattr(i, 'url', '')
            Answer += f"Title: {title}\nDescription: {description}\nURL: {url}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Search failed: {e}"

# Clean up final string formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# System prompt structure
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like current date and time
def Information():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    
    data = "Use This Real-time Information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Fast Realtime Search Engine with live token streaming
def RealtimeSearchEngine(prompt):
    # Load chat history safely
    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)
    except (FileNotFoundError, JSONDecodeError):
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})

    # Perform quick Google search
    search_data = GoogleSearch(prompt)

    try:
        messages_payload = (
            SystemChatBot 
            + [{"role": "system", "content": search_data}]
            + [{"role": "system", "content": Information()}] 
            + messages
        )

        # High-speed model execution
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Ultra-fast model
            messages=messages_payload,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        print("\nAssistant: ", end="", flush=True)

        # Stream chunks directly to terminal for near-instant response feedback
        for chunk in completion:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                Answer += content
                print(content, end="", flush=True)

        print("\n")  # Newline after streaming completes

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save conversation state
        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"\nError: {e}")
        return "Sorry, I ran into an error generating that response."

# Main interactive loop with exit handler
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        
        if prompt.lower().strip() in ["exit", "quit", "stop", "bye"]:
            print("Goodbye!")
            break
            
        RealtimeSearchEngine(prompt)