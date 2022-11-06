from flask import Flask, flash, render_template, url_for, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, UserMixin
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' + os.path.join(base_dir,'Blog2.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'c6a3989cca843a8f5e986a067c8971cd3179fb8b7e40a1adb8a927a55cdeea2e'

db = SQLAlchemy(app)
# db.init_app(app) 
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User <{self.username}>"

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(), nullable=False)
    author_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post <{self.title}, {self.date_posted}>"

class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f"Message <{self.name}, {self.email}>"

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

@app.before_request
def create_tables():
    db.create_all()




@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact')
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        title = request.form.get('title')
        message = request.form.get('message')
        new_message = Message(name=name, email=email, title=title, message=message)
        db.session.add(new_message)
        db.session.commit()
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Me')

@app.route('/protected')
def protected():
    return "The protected page"

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password_hash, password):
            flash('Logged in successfully.', category='success')
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Incorrect password, try again.', category='error')

    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already exists.', category='error')
            return redirect(url_for('register'))
        if email_exists:
            flash('Email already exists.')
            return redirect(url_for('register', category='error'))
        if len(username) < 4:
            flash('Username must be at least 4 characters.', category='error')
            return redirect(url_for('register'))
        if len(first_name) < 2:
            flash('First name must be at least 2 characters.', category='error')
            return redirect(url_for('register'))
        if len(last_name) < 2:
            flash('Last name must be at least 2 characters.', category='error')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', category='error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', category='error')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, first_name=first_name, last_name=last_name, email=email, password_hash=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.', category='success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('home'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user
        new_post = Post(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully.', category='success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        db.session.commit()
        flash('Post updated successfully.', category='success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('create_post.html', title='Update Post', legend='Update Post',  post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully.', category='success')
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)