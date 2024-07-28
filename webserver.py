from flask import Flask, render_template, send_from_directory, redirect, url_for, request, abort
import os
import re
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, "images/favicon.jpg")

@app.route('/article1')
def article1():
    return render_template("article.html")

#This allows you to change the image on the main Breaking News article
@app.route('/breakingnewsimage')
def breakingnewsimage():
    return send_from_directory(app.static_folder, "images/h3show1thumbnail.png")

# Generate new article page
@app.route('/submit')
def submit():
    return render_template('create_article.html')

def hyperlink_urls(text):
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.sub(r'<a href="\1">\1</a>', text)

app.jinja_env.filters['hyperlink'] = hyperlink_urls

@app.route('/submit_article', methods=['POST'])
def submit_article():
    title = request.form['title']
    author = request.form['author']
    date = request.form['date']
    content = request.form['content']
    youtube = request.form['youtube']
    link = '/article/' + title.replace(' ', '-').lower()

    article = {
        'title': title,
        'link': link,
        'author': author,
        'date': date,
        'content': content,
        'youtube': youtube
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
