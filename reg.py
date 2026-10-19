
from pathlib import Path

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


if __name__ == "__main__":
    documents = load_policy_documents()
    chunks = split_into_chunks(documents)

    print("Documents loaded:", len(documents))
    print("Chunks created:", len(chunks))

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i} | Source: {chunk['source']}")
        print(chunk["text"])
