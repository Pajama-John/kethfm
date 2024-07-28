from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/article1')
def article1():
    return render_template("article.html")

#This allows you to change the image on the main Breaking News article
@app.route('/breakingnewsimage')
def breakingnewsimage():
    return send_from_directory(app.static_folder, "images/ThumbnailH3SHow2.jpg")

if __name__ == "__main__":
    app.run(port=666, debug=True)
