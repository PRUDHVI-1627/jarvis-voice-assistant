import asyncio
from random import randint
from PIL import Image
from dotenv import dotenv_values
import os
from time import sleep
from huggingface_hub import InferenceClient

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")

# Define cross-platform directories and paths.
DATA_DIR = "Data"
FRONTEND_FILES_DIR = os.path.join("Frontend", "Files")
IMAGE_GEN_DATA_PATH = os.path.join(FRONTEND_FILES_DIR, "ImageGeneration.data")

# Ensure required directories exist.
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FRONTEND_FILES_DIR, exist_ok=True)

# Initialize Hugging Face Inference Client
client = InferenceClient(api_key=HuggingFaceAPIKey)

# Function to open and display generated images using system default viewer
def open_images(prompt):
    prompt_formatted = prompt.replace(" ", "_")
    Files = [f"{prompt_formatted}{i}.jpg" for i in range(1, 4)]

    for jpg_file in Files:
        image_path = os.path.join(DATA_DIR, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# Helper function to generate a single image using the HF Client
def generate_single_image(prompt: str, seed: int):
    try:
        # Generate PIL Image directly
        image = client.text_to_image(
            prompt=f"{prompt}, high quality, 4k resolution, detailed, seed={seed}",
            model="black-forest-labs/FLUX.1-dev"
        )
        return image
    except Exception as e:
        print(f"Generation error: {e}")
        return None

# Async wrapper for generating 3 images concurrently
async def generate_images(prompt: str):
    tasks = []

    for _ in range(3):
        seed = randint(0, 1000000)
        task = asyncio.to_thread(generate_single_image, prompt, seed)
        tasks.append(task)

    pil_images = await asyncio.gather(*tasks)

    prompt_formatted = prompt.replace(" ", "_")
    success_count = 0

    for i, img in enumerate(pil_images):
        if img is not None:
            file_path = os.path.join(DATA_DIR, f"{prompt_formatted}{i + 1}.jpg")
            img.save(file_path)
            success_count += 1
            
    print(f"Successfully generated {success_count}/3 images.")

# Wrapper function to generate and then display images
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Single-execution block
if __name__ == "__main__":
    if os.path.exists(IMAGE_GEN_DATA_PATH):
        with open(IMAGE_GEN_DATA_PATH, "r", encoding="utf-8") as f:
            Data: str = f.read().strip()

        if "," in Data:
            Prompt, Status = Data.split(",", 1)

            if Status.strip().lower() == "true":
                print(f"Generating 3 Images for prompt: '{Prompt.strip()}'...")
                GenerateImages(prompt=Prompt.strip())

                # Reset status to False after generating
                with open(IMAGE_GEN_DATA_PATH, "w", encoding="utf-8") as f:
                    f.write("False,False")
                
                print("Done! Exiting script.")
            else:
                print("Status is False or empty. No images to generate.")
        else:
            print("Invalid format in ImageGeneration.data. Expected 'Prompt,True'")
    else:
        print(f"File not found: {IMAGE_GEN_DATA_PATH}")