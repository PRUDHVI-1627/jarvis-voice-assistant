import pygame  # Import pygame library for handling audio playback
import random  # Import random for generating random choices
import asyncio  # Import asyncio for asynchronous operations
import edge_tts  # Import edge_tts for text-to-speech functionality
import os  # Import os for file path handling
from dotenv import dotenv_values  # Import dotenv for reading environment variables from a .env file

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "en-US-AvaNeural")  # Default fallback voice if unset

# Cross-platform path definition
SPEECH_FILE_PATH = os.path.join("Data", "speech.mp3")

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    if os.path.exists(SPEECH_FILE_PATH):  # Check if the file already exists
        try:
            os.remove(SPEECH_FILE_PATH)  # Remove old file if present
        except PermissionError:
            pass  # Handle brief file locks safely

    # Create the communicate object to generate speech
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(SPEECH_FILE_PATH)  # Save generated speech as MP3

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    while True:
        try:
            # Convert text to an audio file asynchronously
            asyncio.run(TextToAudioFile(Text))

            # Initialize pygame mixer for audio playback
            pygame.mixer.init()

            # Load the generated speech file into pygame mixer
            pygame.mixer.music.load(SPEECH_FILE_PATH)
            pygame.mixer.music.play()  # Play the audio

            # Loop until the audio is done playing or the function stops
            while pygame.mixer.music.get_busy():
                if func() == False:  # Check if the external function returns False
                    break
                pygame.time.Clock().tick(10)  # Limit loop check to 10 ticks/sec

            return True  # Return True if audio played successfully

        except Exception as e:  # Handle exceptions during process
            print(f"Error in TTS: {e}")
            break

        finally:
            try:
                # Call provided function to signal end of TTS
                func(False)
                pygame.mixer.music.stop()  # Stop audio playback
                pygame.mixer.music.unload()  # Unload file to prevent file lock
                pygame.mixer.quit()  # Quit pygame mixer safely
            except Exception as e:
                print(f"Error in finally block: {e}")

# Function to manage Text-to-Speech with extra responses for long text
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")  # Split text into sentences

    # List of predefined responses when text is long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # Summarize spoken audio if text is longer than 4 sentences and 250 characters
    if len(Data) > 4 and len(Text) >= 250:
        TTS(". ".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

# Main execution loop for testing
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        if user_input.lower().strip() in ["exit", "quit", "stop", "bye"]:
            print("Goodbye!")
            break
        TextToSpeech(user_input)