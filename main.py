from flask import Flask, flash, abort, g, jsonify, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from posts import Posts
from projects import Projects
import json
import datetime
import smtplib
import os
from datetime import date
from bleach_security import strip_invalid_html
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from forms import CreatePostForm, LoginForm, UserForm, CommentForm
from models import User, BlogPost, app, db, Comment, ProjectPost
from flask_ckeditor import CKEditor, CKEditorField
from functools import wraps
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap(app)
ckeditor = CKEditor(app)
gravatar = Gravatar(app, size=30, default='retro')


admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(BlogPost, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(ProjectPost, db.session))

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        return abort(403)
        # return jsonify(error={"No Permission": "Sorry, this user is not an Admin."})
    return decorated_function


YEAR = datetime.datetime.now().year
my_second_gmail = os.environ.get('SMTP_GMAIL')
second_gmail_app_password = os.environ.get('GMAIL_PASS')
my_gmail = os.environ.get('S_GMAIL')
gmail_app_password = os.environ.get('S_GMAIL_PASS')

posts = json.load(open('static/blog-data.json'))
post_obj = []
for post in posts:
    obj = Posts(post["id"], post["title"], post["subtitle"], post["body"])
    post_obj.append(obj)


'''
Project pages display 
'''
def project(page, proj_type='mini'):
    per_page = 3
    return ProjectPost.query.filter(ProjectPost.type == proj_type).paginate(page=page, per_page=per_page, error_out=False)

@app.route('/')
def home(page=1):  # put application's code here
    return render_template('index.html', year=YEAR, name=current_user, project_posts=project(page, proj_type='mini'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    error = None
    message = "Contact Me"
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        email_message = request.form['message']
        send_email(name, email, subject, email_message)
        message = 'Successfully sent your message!'

    return render_template('contact.html', year=YEAR, message=message)


# Take Mini, Capstone, Experience as inputs
@app.route('/about/<int:page>', methods=["POST", "GET"])
def about(page):
    project_descriptions = {
        'mini': "Mini-Projects by definition are small, usually these projects take me one to two days.\n " \
                                  "They display my perspicacity in a specific topic.",
        'capstone': 'The Capstone projects are a display of my ability to combine technologies',
        'experience': "Work Experience I've accumulated over the past 4 years as a professional software engineer"
    }
    proj_type = 'mini'
    if request.method == 'POST':
        proj_type = request.form['projectType']
        print(proj_type)
        combined_objects = {}
        projects = ProjectPost.query.filter_by(type=proj_type).all()
        for obj in projects:
            combined_objects.update(obj.__dict__)
        print(obj.title)
        return render_template('about.html', year=YEAR,
                               project_posts=project(page=1, proj_type=proj_type),
                               project_type=proj_type.upper(),
                               project_description=project_descriptions[proj_type])

    return render_template('about.html', year=YEAR,
                           project_posts=project(page, proj_type=proj_type),
                           project_type=proj_type.upper(),
                           project_description=project_descriptions[proj_type])


def send_email(name, email, subject, email_message):
    sent_message = f'Subject:{subject}\n \n Name: {name} \nEmail: {email} \n Message:{email_message}'.encode('utf-8')
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()  # secures the connection by encrypting
        connection.login(user=my_second_gmail, password=second_gmail_app_password)
        connection.sendmail(
            from_addr=my_second_gmail,
            to_addrs=my_gmail,
            msg=sent_message
        )

@app.route('/blog')
def blog():
    blogs = db.session.query(BlogPost).all()
    return render_template('blog.html', year=YEAR, blog_posts=[blog.to_dict() for blog in blogs], name=current_user)


@app.route('/blog/<int:post>', methods=['POST', 'GET'])
def blog_post(post):
    comments = db.session.query(Comment).all()
    form = CommentForm()
    selected_blog = BlogPost.query.get(post)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(
            comment_text=strip_invalid_html(form.comment.data),
            author_id=current_user.id,
            post_id=post
        )
        db.session.add(new_comment)
        db.session.commit()
        return render_template('blog_post.html', blog=selected_blog, form=form, comments=comments)
    return render_template('blog_post.html', blog=selected_blog, form=form, comments=comments)

#  Projects, will show a demo of a project on each tab.... brrrr its connected by ID!
@app.route('/projects/<int:project_id>')
def project_page(project_id, page=1):
    selected_project = ProjectPost.query.get(project_id)
    return render_template('project_post.html', project=selected_project, year=YEAR, projects=project(page, proj_type='capstone'))

@app.route('/delete/<int:post_id>')
@login_required
@admin_required
def delete_post(post_id):
    delete_post = BlogPost.query.get(post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('blog'))

# WTForms don't accept PUT, PATCH or Delete, so we POST
@app.route('/edit-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    print(post.title)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        author=post.author,
        img_url=post.img_url
    )
    if edit_form.validate_on_submit():
        if post:
            post.title = strip_invalid_html(edit_form.title.data)
            post.subtitle = strip_invalid_html(edit_form.subtitle.data)
            post.img_url = strip_invalid_html(edit_form.img_url.data)
            post.body = strip_invalid_html(edit_form.body.data)
            # print("NEW DATA: ", strip_invalid_html(edit_form.body.data))
            db.session.commit()
            return redirect(url_for("blog", post_id=post.id))

    return render_template('edit-post.html', form=edit_form)


@login_required
@app.route('/new-post', methods=['POST', 'GET'])
@admin_required
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        print("create new blog post")
        new_post = BlogPost(
            title=strip_invalid_html(request.form.get("title")),
            subtitle=strip_invalid_html(request.form.get("subtitle")),
            author_id=current_user.id,
            img_url=strip_invalid_html(request.form.get("img_url")),
            body=strip_invalid_html(request.form.get("body")),
            date=date.today().strftime("%B %d, %Y"),
        )
        try:
            db.session.add(new_post)
            db.session.commit()
        except Exception as error:
            print("Doesn't exist")
        return redirect(url_for("blog"))
    return render_template('make-post.html', form=form)


@login_required
@app.route('/register', methods=["POST", "GET"])
def register():
    form = UserForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            error='That email already exists.'
            return render_template('register.html', form=form, error=error)
        else:
            new_user = User(
                email=form.email.data,
                name=form.name.data,
            password=generate_password_hash
                (
                    password=form.password.data,
                    method='pbkdf2:sha256',
                    salt_length=8
                )
            )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template('register.html', form=form)


@login_required
@app.route('/login', methods=["POST", "GET"])
def login():
    error = None
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        elif user == error:
            error = 'That email does not exist, please try again'
        elif user and not check_password_hash(user.password, form.password.data):
            error = 'Password incorrect, please try again.'
            # return redirect(url_for('login'))
    return render_template("login.html", form=form, error=error)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html', year=YEAR, logged_in=False)






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1122)


