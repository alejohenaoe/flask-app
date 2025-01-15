from flask import Flask, render_template, flash, redirect, url_for
from forms import LoginForm, RegisterForm
from models import db, User

# App initialization
app = Flask(__name__)

# App configuration
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fhData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database initialization
db.init_app(app)

# #Crear las tablas
# with app.app_context():
#     db.create_all()

# Routes definition
@app.route('/', methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        return 'Login requested for user {}'.format(login_form.username)
    return render_template('index.html', form=login_form)

@app.route('/login')
def login():
    pass


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User(
            username=register_form.username.data,
            name = register_form.name.data,
            password = register_form.set_password(register_form.password.data)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=register_form)