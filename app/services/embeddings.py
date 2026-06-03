from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings


def generate_query_embedding(query: str) -> list[float]:
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=query
    )
    return result.embeddings[0].values
