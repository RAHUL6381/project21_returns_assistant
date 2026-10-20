from flask import Flask, render_template, request, jsonify
from return_checker import check_return_eligibility
from rag import load_rag_resources, answer_question

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        category = request.form.get("category")
        delivery_date = request.form.get("delivery_date")
        request_date = request.form.get("request_date")
        unused = request.form.get("unused") == "yes"
        tags_attached = request.form.get("tags_attached") == "yes"

        result = check_return_eligibility(
            category,
            delivery_date,
            request_date,
            unused,
            tags_attached
        )

    return render_template("index.html", result=result)


rag_model, faiss_index, policy_chunks = load_rag_resources()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    conversation_history = data.get("history", [])

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    if not isinstance(conversation_history, list):
        conversation_history = []

    conversation_history = [
    item for item in conversation_history
    if isinstance(item, dict)
    and isinstance(item.get("question"), str)
    and isinstance(item.get("answer"), str)
    ][-4:]

    try:
        answer = answer_question(
        question,
        rag_model,
        faiss_index,
        policy_chunks,
        conversation_history
    )

        return jsonify({
            "question": question,
            "answer": answer
        })

    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({
            "error": "Sorry, something went wrong. Please try again."
        }), 500




if __name__ == "__main__":
    app.run(debug=True)
