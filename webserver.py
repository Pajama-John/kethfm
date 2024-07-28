from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/article1')
def article1():
    return render_template("article.html")

if __name__ == "__main__":
    app.run(port=666, debug=True)
