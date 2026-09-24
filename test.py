from dotenv import load_dotenv
import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

print("Starting LangChain Gemini test...")

start = time.time()

model = ChatGoogleGenerativeAI(
    model="gemini-flash-lite-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

response = model.invoke(
    "Reply with only: Hello"
)

print("Response received:")
print(response.content)

print(f"Time taken: {time.time() - start:.2f} seconds")