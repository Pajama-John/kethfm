from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Welcome to Kethfm.com!</h1><p>This is a placeholder page.</p>"

if __name__ == "__main__":
    app.run(debug=True)
