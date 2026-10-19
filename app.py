from flask import Flask, render_template, request
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

        print(result)

    return render_template("index.html", result=result)


rag_model, faiss_index, policy_chunks = load_rag_resources()

@app.route("/chat", methods=["POST"])
def chat():
    question = request.form.get("question", "").strip()

    if not question:
        return render_template(
            "index.html",
            result=None,
            chat_answer="Please enter a question."
        )

    try:
        answer = answer_question(
            question,
            rag_model,
            faiss_index,
            policy_chunks
        )
    except Exception:
        app.logger.exception("Chat request failed")
        answer = "Sorry, I couldn't process your question. Please try again."

    return render_template(
        "index.html",
        result=None,
        chat_answer=answer,
        question=question
    )



if __name__ == "__main__":
    app.run(debug=True)
