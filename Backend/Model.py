import cohere  # Import the Cohere library for AI services.
from rich import print  # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values  # Import dotenv to load environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve API key.
CohereAPIKey = env_vars.get("CohereAPIKey")

# Create a Cohere client using the provided API key.
co = cohere.Client(api_key=CohereAPIKey)

# Define a list of recognized function keywords for task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister'.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down, etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Define chat history for context
ChatHistory = [
    {"role": "user", "content": "how are you?"},
    {"role": "assistant", "content": "general how are you?"},
    {"role": "user", "content": "do you like pizza?"},
    {"role": "assistant", "content": "general do you like pizza?"},
    {"role": "user", "content": "open chrome and tell me about mahatma gandhi."},
    {"role": "assistant", "content": "open chrome, general tell me about mahatma gandhi."},
    {"role": "user", "content": "open chrome and firefox"},
    {"role": "assistant", "content": "open chrome, open firefox"},
    {"role": "user", "content": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "assistant", "content": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "user", "content": "chat with me."},
    {"role": "assistant", "content": "general chat with me."}
]

# Main decision-making function
def FirstLayerDMM(prompt: str = "test"):
    try:
        # Construct messages payload for Cohere API
        messages_payload = [
            {"role": "system", "content": preamble}
        ] + ChatHistory + [
            {"role": "user", "content": prompt}
        ]

        # Call Cohere Streaming API
        stream = co.chat_stream(
            model='command-r-plus',
            messages=messages_payload,
            temperature=0.7
        )

        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        # Process and clean up output string
        response = response.replace("\n", "")
        response_tasks = response.split(",")

        # Strip leading/trailing whitespaces
        response_tasks = [i.strip() for i in response_tasks]

        # Filter valid tasks matching keyword prefixes
        filtered_tasks = []
        for task in response_tasks:
            for func in funcs:
                if task.startswith(func):
                    filtered_tasks.append(task)  # Add valid task to filtered list

        return filtered_tasks if filtered_tasks else [f"general {prompt}"]

    except Exception as e:
        print(f"[bold red]Error in FirstLayerDMM:[/bold red] {e}")
        return [f"general {prompt}"]

# Entry point for testing
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower().strip() in ["exit", "quit", "stop"]:
            break
        print(FirstLayerDMM(user_input))