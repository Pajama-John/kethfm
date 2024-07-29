from flask import Flask, render_template, send_from_directory, redirect, url_for, request, abort
from werkzeug.utils import secure_filename
from datetime import datetime

import os
import re
import json
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/')
def home():
    featured_article = None
    featured_path = os.path.join('data', 'featured.json')

    if os.path.exists(featured_path):
        with open(featured_path, 'r') as f:
            featured_article = json.load(f)

    return render_template("index.html", featured_article=featured_article)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, "images/favicon.jpg")

@app.route('/article1')
def article1():
    return render_template("article.html")

# Generate new article page
@app.route('/submit')
def submit():
    return render_template('create_article.html')

def hyperlink_urls(text):
    url_pattern = re.compile(r'(https?://\S+)')
    return url_pattern.sub(r'<a href="\1">\1</a>', text)

app.jinja_env.filters['hyperlink'] = hyperlink_urls

# def latest_episode_section():
    

#This allows you to change the image on the main Breaking News article
@app.route('/breakingnewsimage')
def breakingnewsimage():
    featured_path = os.path.join('data', 'featured.json')

    if os.path.exists(featured_path):
        print("exists")
        with open(featured_path, 'r') as f:
            featured_article = json.load(f)
            thumbnail_path = featured_article.get('thumbnail')
            print(thumbnail_path)
            if thumbnail_path and os.path.exists(thumbnail_path):
                return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(thumbnail_path))

    # Fallback to default image if no featured image is set
    print("Fallback image used")
    return send_from_directory(app.static_folder, "images/middle-finger-emoji-1368x2048-03zmpcju.png")



@app.route('/submit_article', methods=['POST'])
def submit_article():
    title = request.form['title']
    author = request.form['author']
    date = request.form['date']
    content = request.form['content']
    youtube = request.form['youtube']
    thumbnail = request.files.get('thumbnail')  # Use .get to avoid KeyError
    link = '/article/' + title.replace(' ', '-').lower()

    article = {
        'title': title,
        'link': link,
        'author': author,
        'date': date,
        'content': content,
        'youtube': youtube,
        'thumbnail': ''
    }
    
    if thumbnail and thumbnail.filename != '':
        filename = secure_filename(thumbnail.filename)
        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        thumbnail.save(thumbnail_path)
        article['thumbnail'] = thumbnail_path.replace('\\', '/')

    
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

@app.route("/submit-featured")
def submit_featured():
    data_folder = 'data'
    articles = []

    for filename in os.listdir(data_folder):
        if filename == "featured.json":
            continue
        elif filename.endswith('.json'):
            filepath = os.path.join(data_folder, filename)
            with open(filepath, 'r') as f:
                article = json.load(f)
                article['filename'] = filename
                articles.append(article)

    # Sort articles by date, most recent first
    articles.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

    return render_template("featured_form.html", articles=articles)

@app.route("/set-featured", methods=["POST"])
def set_featured():
    selected_file = request.form['articles']
    source_path = os.path.join("data", selected_file)
    destination_path = os.path.join("data", 'featured.json')

    # Copy the selected file to featured.json
    shutil.copyfile(source_path, destination_path)

    return redirect("/")


if __name__ == "__main__":
    app.run(port=666, debug=True)
