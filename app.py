from flask import Flask, render_template, request
from return_checker import check_return_eligibility


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


if __name__ == "__main__":
    app.run(debug=True)
