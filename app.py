
from flask import Flask, render_template, request

app = Flask(__name__)



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        category = request.form.get("category")
        delivery_date = request.form.get("delivery_date")
        request_date = request.form.get("request_date")
        unused = request.form.get("unused") == "yes"
        tags_attached = request.form.get("tags_attached") == "yes"

        print("Category:", category)
        print("Delivery Date:", delivery_date)
        print("Request Date:", request_date)
        print("Unused:", unused)
        print("Tags Attached:", tags_attached)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
