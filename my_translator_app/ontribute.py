from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contribute")
def contribute():
    return render_template("contribute.html")

if __name__ == "__main__":
    app.run(debug=True)
