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

# Define system message prompt.
System = f"You are {Assistantname}, an AI assistant for {Username}. Provide helpful answers using web results."

# Cross-platform file path definition (works on macOS, Linux, and Windows)
CHAT_LOG_PATH = "Data/ChatLog.json"

# Initialize or fix empty chat log safely
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)
except (FileNotFoundError, JSONDecodeError):
    messages = []
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f, indent=4)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Search failed: {e}"

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Base system prompts
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
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
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    # Load existing chat log safely in read mode ("r")
    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)
    except (FileNotFoundError, JSONDecodeError):
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})

    # Perform Google search
    search_data = GoogleSearch(prompt)

    try:
        # Construct message payload dynamically (prevents global list corruption)
        messages_payload = (
            SystemChatBot 
            + [{"role": "system", "content": search_data}]
            + [{"role": "system", "content": Information()}] 
            + messages
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated supported model
            messages=messages_payload,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
        
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        # Save updated conversation log back using write mode ("w")
        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I ran into an error generating that response."

# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        
        # Exit switch to cleanly terminate the program
        if prompt.lower().strip() in ["exit", "quit", "stop", "bye"]:
            print("Goodbye!")
            break
            
        print(RealtimeSearchEngine(prompt))