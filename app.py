from flask import Flask, render_template
from posts import Posts
import json
import datetime
app = Flask(__name__)
YEAR = datetime.datetime.now().year

posts = json.load(open('static/blog-data.json'))
post_obj = []
for post in posts:
    obj = Posts(post["id"], post["title"], post["subtitle"], post["body"])
    post_obj.append(obj)


@app.route('/')
def home():  # put application's code here
    return render_template('index.html', year=YEAR)


@app.route('/contact')
def contact():
    return render_template('contact.html', year=YEAR)


@app.route('/blog')
def blog():
    return render_template('blog.html', year=YEAR, blog_posts=post_obj)

@app.route('/blog/<int:post>')
def blog_post(post):
    selected_blog = 0
    for blog in post_obj:
        if blog.id == post:
            selected_blog = blog
    return render_template('blog_post.html', blog=selected_blog)


@app.route('/about')
def about():
    return render_template('about.html', year=YEAR)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1555)
