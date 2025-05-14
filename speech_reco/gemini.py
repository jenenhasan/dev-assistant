from google import genai
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the API key from the environment variable
API_KEY = os.getenv("API_KEY")

# Check if the API key is missing or invalid
if not API_KEY:
    print("Error: API key is missing or invalid.")
    exit()

# Initialize the genai client with the API key
client = genai.Client(api_key=API_KEY)

class GeminiAPI:
    def __init__(self):
        self.model = "gemini-2.0-flash"  # Use the correct model name
        self.api_key = client  # Use the initialized client
    
    def get_answer(self, query: str) -> str:
        try:
            # Generate content using the API client and the given model
            response = self.api_key.models.generate_content(
                model=self.model,
                contents=query,
               
              

               
            )
            return response.text  # Return the generated content
        except Exception as e:
            print(f"Error: {e}")
            return "There was an error processing your request."

if __name__ == "__main__":
    gemini = GeminiAPI()
    question = "take about france?"
    answer = gemini.get_answer(f"answer the question in short way : {question}")
    print(f"Question: {question}")
    print(f"Answer: {answer}")
