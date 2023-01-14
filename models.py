from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from sqlalchemy_utils import  ChoiceType


## CHOICES IMPORT
## https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.choice

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfbA606donzWlsih'
Bootstrap(app)
app = Flask(__name__)

## CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    # act like a list of BlogPost objects attached to each User.
    # "author" refers to author property in BlogPost class.
    posts = relationship("BlogPost", back_populates="author")

    # act like a list of Comment objects attached to each User.
    comments = relationship("Comment", back_populates="comment_author")


## Create Project Class
class ProjectPost(db.Model):

    TYPES  = [
        ('mini', 'Mini'),
        ('capstone', 'Capstone'),
        ('experience', 'Experience')
    ]

    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250),  nullable=False)
    updated_date = db.Column(db.String(250),  nullable=False)
    body = db.Column(db.Text,  nullable=False)
    url = db.Column(db.String(150), nullable=False)
    type = db.Column(ChoiceType(TYPES), nullable=False)

##CONFIGURE Blog Table
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="post")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250),  unique=True, nullable=False)
    date = db.Column(db.String(250),  nullable=False)
    body = db.Column(db.Text,  nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}
        dict = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dict[column.name] = getattr(self, column.name)
        return dict


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)

    # ForeignKey, "users.id" the users refers to the tablename of User
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")

    # ForeignKey "blog_posts" the blog_post refers to the tablename of BlogPost
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    post = relationship("BlogPost", back_populates="comments")

    comment_text = db.Column(db.String(250),  nullable=False)



## CREATE DATABASE
# with app.app_context():
#     db.create_all()