from flask import Flask, render_template, send_from_directory, redirect, url_for, request, abort
from werkzeug.utils import secure_filename
from datetime import datetime

import os
import re
import json
import shutil
import pickle

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def latest_episode_section():
    with open("data/latest.pickle", "rb") as f:
        latest = pickle.load(f)
    return latest

@app.route('/search')
def search():
    tags = request.args.get('tags')
    if not tags:
        return abort(400, description="Tags parameter is required")

    # Split tags by comma and convert to lowercase
    tag_list = [tag.strip().lower() for tag in tags.split(',')]

    # Load all articles
    articles = load_articles()

    # Filter articles by tags (case-insensitive)
    matching_articles = []
    for article in articles:
        article_tags = [t.lower() for t in article['tags']]
        if all(tag in article_tags for tag in tag_list):
            matching_articles.append(article)

    return render_template('search_results.html', tags=tag_list, articles=matching_articles)


@app.route('/submit-latest')
def latest():
    articles = load_articles()
    return render_template("latest_form.html", articles=articles)

@app.route('/set-latest', methods=['POST'])
def set_latest():
    latest_articles = dict(request.form)
    with open("data/latest.pickle", "wb") as f:
        pickle.dump(latest_articles, f)
    return redirect("/")

@app.route('/')
def index():
    featured_article = None
    featured_path = os.path.join('data', 'featured.json')

    # Load latest articles
    latest_articles = latest_episode_section()
    
    if os.path.exists(featured_path):
        with open(featured_path, 'r') as f:
            featured_article = json.load(f)
    
    # Load all articles
    articles = {article['filename']: article for article in load_articles()}
    
    return render_template("index.html", featured_article=featured_article, latest_articles=latest_articles, articles=articles)

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

#This allows you to change the image on the main Breaking News article
@app.route('/breakingnewsimage')
def breakingnewsimage():
    featured_path = os.path.join('data', 'featured.json')

    if os.path.exists(featured_path):
        with open(featured_path, 'r') as f:
            featured_article = json.load(f)
            thumbnail_path = featured_article.get('thumbnail')
            if thumbnail_path and os.path.exists(thumbnail_path):
                return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(thumbnail_path))

    # Fallback to default image if no featured image is set
    return send_from_directory(app.static_folder, "images/middle-finger-emoji-1368x2048-03zmpcju.png")

def get_meta_description(content, length=160):
    # Remove any HTML tags from the content
    text = re.sub('<[^<]+?>', '', content)
    # Return the first 'length' characters
    return text[:length] + '...' if len(text) > length else text

app.jinja_env.globals.update(get_meta_description=get_meta_description)

@app.route('/submit_article', methods=['POST'])
def submit_article():
    pprint(dict(request.form))
    title = request.form['title']
    author = request.form['author']
    date = request.form['date']
    content = request.form['content']
    youtube = request.form['youtube']
    tags = [x.strip() for x in request.form['tags'].split(',')]
    thumbnail = request.files.get('thumbnail')  # Use .get to avoid KeyError
    
    # Remove non-alphanumeric characters from the title
    sanitized_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title)

    link = '/article/' + sanitized_title.lower()

    article = {
        'title': title,
        'link': link,
        'author': author,
        'date': date,
        'content': content,
        'youtube': youtube,
        'tags': tags,
        'thumbnail': ''
    }
    
    if thumbnail and thumbnail.filename != '':
        filename = secure_filename(thumbnail.filename)
        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        thumbnail.save(thumbnail_path)
        article['thumbnail'] = thumbnail_path.replace('\\', '/')

    # Save the article as a JSON file
    filename = sanitized_title.lower() + '.json'
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
        if filename == "featured.json":
            continue
        if filename.endswith('.json'):
            with open(os.path.join('data', filename), 'r') as f:
                article = json.load(f)
                article['filename'] = filename
                articles.append(article)
    return articles

@app.route('/article/<string:title>')
def article(title):
    # Sanitize the title to match the filename
    sanitized_title = re.sub(r'[^a-zA-Z0-9_-]', '_', title).lower()
    filename = sanitized_title + '.json'
    
    filepath = os.path.join('data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            article = json.load(f)
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

@app.route('/dev-tools')
def dev_tools():
    return render_template('dev_tools.html')

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    files = [f for f in os.listdir("data") if f.endswith('.json') and f != 'featured.json']
    json_data = None
    selected_file = None

    if request.method == 'POST' and 'file' in request.form:
        selected_file = request.form['file']
        with open(os.path.join("data", selected_file), 'r') as file:
            json_data = json.load(file)

    return render_template('edit.html', files=files, json_data=json_data, selected_file=selected_file)

@app.route('/update', methods=['POST'])
def update():
    filename = request.form['filename']
    file_path = os.path.join("data", filename)

    # Load existing data to ensure all fields are preserved
    with open(file_path, 'r') as file:
        existing_data = json.load(file)

    # Sanitize new title
    new_title = request.form['title']
    sanitized_title = re.sub(r'[^a-zA-Z0-9_-]', '_', new_title).lower()
    new_link = '/article/' + sanitized_title
    
    new_data = {
        'title': new_title,
        'link': new_link,
        'author': existing_data.get('author', ''),
        'date': existing_data.get('date', ''),
        'content': request.form['content'],
        'youtube': existing_data.get('youtube', ''),
        'tags': request.form['tags'].split(','),
        'thumbnail': request.form['thumbnail']
    }

    # Handle thumbnail file upload
    if 'thumbnail-file' in request.files:
        file = request.files['thumbnail-file']
        if file.filename != '':
            thumbnail_path = os.path.join('static/uploads/', file.filename)
            file.save(thumbnail_path)
            new_data['thumbnail'] = thumbnail_path

    # New filename based on sanitized title
    new_filename = sanitized_title + '.json'
    
    # Delete the old file if the name is changed
    if filename != new_filename:
        os.remove(file_path)
        file_path = os.path.join("data", new_filename)

    # Save new data
    with open(file_path, 'w') as file:
        json.dump(new_data, file, indent=4)

    return redirect(new_link)

if __name__ == "__main__":
    app.run(port=666, debug=True)
