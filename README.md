# Returns Assistant

A simple Flask web app that helps customers check return eligibility and ask policy-related questions about returns, exchanges, and refunds.

## Overview

This project combines:

- a rule-based return eligibility checker
- a policy chatbot powered by semantic search (FAISS + sentence embeddings)
- a lightweight web interface for customer support

It is designed to answer common store policy questions based on the policy documents stored in the `data/` folder.

## Features

- Check whether a product is eligible for return
- Validate return conditions such as product category, delivery date, request date, unused status, and tag status
- Answer customer questions using retrieval-augmented generation (RAG)
- Keep recent chat history for follow-up questions
- Provide a simple web UI for support interactions

## Tech Stack

- Python
- Flask
- FAISS
- SentenceTransformers
- Google Gemini API

## Project Structure

```text
project21_returns_assistant/
├── app.py                  # Flask application entry point
├── rag.py                 # Policy retrieval and chatbot logic
├── return_checker.py      # Return eligibility rules
├── data/                  # Store policy text files and indexed data
├── static/                # CSS and frontend JS assets
├── templates/             # HTML templates
├── .env                   # Environment variables (for API key)
├── .gitignore
└── README.md
```

## Setup

1. Clone or download the project.
2. Open a terminal in the project folder.
3. Create and activate a virtual environment if needed.
4. Install dependencies:

```bash
pip install flask sentence-transformers faiss-cpu python-dotenv google-genai
```

5. Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run the App

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Notes

- The app is intended for policy support and informational guidance.
- It does not submit return requests or guarantee refund approval.
- Policy answers are based on the stored documents in the `data/` folder and the configured Gemini model.

## License

This project is provided for educational and demo purposes.
