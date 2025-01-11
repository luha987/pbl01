from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Define post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('posts', lazy=True))

# Define log data model
class LogData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(80), nullable=False)
    key = db.Column(db.String(80), nullable=False)
    txt = db.Column(db.String(80), nullable=False)
    session = db.Column(db.String(80), nullable=False)
    ipaddr = db.Column(db.String(80), nullable=False)
    app = db.Column(db.String(80), nullable=False)
    time = db. Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    # Display team member name, show reg and sign in buttons
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('profile', username=username))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form['text']
        new_post = Post(text=text, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('create_post.html')

@app.route('/log_data', methods=['GET', 'POST'])
@login_required
def log_data():
    if request.method == 'POST':
        uuid = request.form['uuid']
        key = request.form['key']
        txt = request.form['txt']
        session = request.form['session']
        ipaddr = request.form['ipaddr']
        app = request.form['app']
        new_log = LogData(uuid=uuid, key=key, txt=txt, session=session, ipaddr=ipaddr, app=app)
        db.session.add(new_log)
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
    return render_template('log_data.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)