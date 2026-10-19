
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Folder containing the policy documents
DATA_DIR = Path(__file__).parent / "data"


def load_policy_documents():
    documents = {}

    policy_files = [
        "return_policy.txt",
        "exchange_policy.txt",
        "refund_procedure.txt"
    ]

    for filename in policy_files:
        file_path = DATA_DIR / filename

        with open(file_path, "r", encoding="utf-8") as file:
            documents[filename] = file.read()

    return documents


def split_into_chunks(documents, chunk_size=500, overlap=50):
    chunks = []

    for filename, text in documents.items():
        start = 0

        while start < len(text):
            end = start + chunk_size

            chunks.append({
                "source": filename,
                "text": text[start:end]
            })

            start += chunk_size - overlap

    return chunks


def generate_embeddings(chunks):
    # Load a pretrained embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Extract text from chunks
    texts = [chunk["text"] for chunk in chunks]

    # Convert text into numerical vectors
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return model, embeddings


def store_embeddings(embeddings, chunks):
    # Create a FAISS index for normalized embeddings
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)

    # Store embeddings as 32-bit floating-point numbers
    index.add(np.asarray(embeddings, dtype=np.float32))

    # Create the data folder if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save the FAISS index
    faiss.write_index(index, str(DATA_DIR / "policy.index"))

    # Save chunk text and source information
    with open(DATA_DIR / "policy_chunks.json", "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    return index


def embed_question(question, model):
    # Convert the user's question into a numerical vector
    question_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return np.asarray(question_embedding, dtype=np.float32)


def retrieve_relevant_chunks(question, model, index, chunks, top_k=3):
    # Convert the question into an embedding
    question_embedding = embed_question(question, model)

    # Search FAISS for the most similar chunks
    scores, indices = index.search(question_embedding, top_k)

    # Return the matching chunks with similarity scores
    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            results.append({
                "text": chunks[idx]["text"],
                "source": chunks[idx]["source"],
                "score": float(score)
            })

    return results


def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}"
        for chunk in retrieved_chunks
    )

    prompt = f"""
You are an Online Store Returns Policy Assistant.

Answer the user's question using ONLY the policy context below.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain the answer, clearly say:
   "I could not find this information in the provided return policies."
3. Do not invent policies, refund statuses, or stock availability.
4. Keep answers clear and concise.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text



def load_rag_resources():
    model = SentenceTransformer("all-MiniLM-L6-v2")

    index = faiss.read_index(
        str(DATA_DIR / "policy.index")
    )

    with open(
        DATA_DIR / "policy_chunks.json",
        "r",
        encoding="utf-8"
    ) as file:
        chunks = json.load(file)

    return model, index, chunks


def answer_question(question, model, index, chunks):
    relevant_chunks = retrieve_relevant_chunks(
        question, model, index, chunks, top_k=3
    )

    if not relevant_chunks:
        return "I could not find relevant information in the provided return policies."

    return generate_answer(question, relevant_chunks)



if __name__ == "__main__":
    documents = load_policy_documents()
    chunks = split_into_chunks(documents)

    model, embeddings = generate_embeddings(chunks)
    index = store_embeddings(embeddings, chunks)

    print("Documents loaded:", len(documents))
    print("Chunks created:", len(chunks))
    print("Embeddings shape:", embeddings.shape)
    print("FAISS index saved successfully!")

    
    question = "When does refund processing begin?"

    results = retrieve_relevant_chunks(
        question, model, index, chunks, top_k=3
    )

    for result in results:
        print("\nSource:", result["source"])
        print("Similarity:", round(result["score"], 3))
        print("Text:", result["text"])
