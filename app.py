from flask import Flask, render_template, flash, redirect, url_for
from forms import LoginForm, RegisterForm, EditUserForm
from models import db, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# App initialization
app = Flask(__name__)
login_manager = LoginManager()

# App configuration
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fhData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Components initialization
db.init_app(app)
login_manager.init_app(app)

# Redirecting to login page and message to not logged in users
login_manager.login_view = 'home'
login_manager.login_message = 'You need to be logged in to access this page'

# loading user from database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# #Crear las tablas
# with app.app_context():
#     db.create_all()

# Routes definition
@app.route('/', methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('logged_in', username=current_user.username))
        else:
            flash('User not found', 'error')
            return redirect(url_for('home'))
    return render_template('index.html', form=login_form)

@app.route('/<username>', methods=['GET', 'POST'])
@login_required
def logged_in(username):
    if username != current_user.username:
        flash('You need to log in first', 'info')
        return redirect(url_for('home'))
    return render_template('logged_in.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User(
            username=register_form.username.data,
            name = register_form.name.data
        )
        new_user.set_password(register_form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=register_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/edit/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if username != current_user.username:
        flash('You need to log in first', 'error')
        return redirect(url_for('home'))
    
    edit_form = EditUserForm()

    if edit_form.validate_on_submit():
        current_user.username = edit_form.username.data
        current_user.name = edit_form.name.data
        current_user.password = edit_form.password.data

        # Verifying if the user has changed the username, name or password
        if current_user.username:
            current_user.username = edit_form.username.data
        if current_user.name:
            current_user.name = edit_form.name.data
        if current_user.password:
            current_user.set_password(edit_form.password.data)
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('logged_in', username=current_user.username))

    return render_template('edit_user.html', edit_form=edit_form)