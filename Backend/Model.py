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
# Updated preamble section in Backend/Model.py
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram'.
*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'realtime ( query )' if a query asks about ANY specific individual, celebrity, public figure, sports personality, company, news event, or real-time info. Examples:
   - 'who is elon musk' -> 'realtime who is elon musk'
   - 'who is virat kohli' -> 'realtime who is virat kohli'
   - 'what is today's news' -> 'realtime what is today's news'

-> Respond with 'general ( query )' ONLY if the query is purely conversational, mathematical, educational concepts, or standard greetings. Examples:
   - 'how are you' -> 'general how are you'
   - 'what is photosynthesis' -> 'general what is photosynthesis'
   - 'solve 2+2' -> 'general solve 2+2'

-> Respond with 'open (application name)' for opening apps.
-> Respond with 'close (application name)' for closing apps.
-> Respond with 'play (song name)' for playing music.
-> Respond with 'generate image (prompt)' for generating images.
-> Respond with 'system (task)' for volume/system controls.
*** If the user is saying goodbye respond with 'exit'. ***
"""

# Predefined chat history for context
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

# Main decision-making function
def FirstLayerDMM(prompt: str = "test"):
    try:
        # Call Cohere Streaming API with compatible keyword arguments
        stream = co.chat_stream(
            model='command-r-08-2024',
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            preamble=preamble
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
                    filtered_tasks.append(task)

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