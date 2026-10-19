
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

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



if __name__ == "__main__":
    documents = load_policy_documents()
    chunks = split_into_chunks(documents)

    model, embeddings = generate_embeddings(chunks)
    index = store_embeddings(embeddings, chunks)

    print("Documents loaded:", len(documents))
    print("Chunks created:", len(chunks))
    print("Embeddings shape:", embeddings.shape)
    print("FAISS index saved successfully!")