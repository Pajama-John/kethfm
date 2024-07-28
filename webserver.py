from flask import Flask, render_template, send_from_directory, redirect, url_for, request
import os
import json

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

# Generate new article page
@app.route('/submit')
def submit():
    return render_template('create_article.html')

@app.route('/submit_article', methods=['POST'])
def submit_article():
    title = request.form['title']
    author = request.form['author']
    date = request.form['date']
    content = request.form['content']
    
    link = '/article/' + title.replace(' ', '-').lower()
    
    article = {
        'title': title,
        'author': author,
        'date': date,
        'link': link,
        'content': content
    }
    
    # Save the article as a JSON file
    filename = title.replace(' ', '-').lower() + '.json'
    with open(os.path.join('data', filename), 'w') as f:
        json.dump(article, f)
    
    # Reload articles
    global articles
    articles = load_articles()
    
    return redirect(link)


# Code for handling and serving articles
def load_articles():
    articles = []
    for filename in os.listdir('data'):
        if filename.endswith('.json'):
            with open(os.path.join('data', filename)) as f:
                articles.append(json.load(f))
    return articles

@app.route('/article/<string:title>')
def article(title):
    articles = load_articles()

    for article in articles:
        if article['title'].replace(' ', '-').lower() == title.lower():
            return render_template('article.html', article=article)
    return "Error"


if __name__ == "__main__":
    app.run(port=666, debug=True)
