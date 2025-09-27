from flask import Flask, render_template, request
from downloader import download_post

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        url = request.form.get("url")
        try:
            message = download_post(url)
        except Exception as e:
            message = f"Error: {e}"
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)