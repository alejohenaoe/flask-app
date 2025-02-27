from flask import Flask, render_template, flash, redirect, url_for, request
from forms import LoginForm, RegisterForm, EditUserForm, DeleteUserForm, TransactionForm
from models import db, User, Income, Outcome
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
import os

# Data Analysis libraries
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# App initialization
app = Flask(__name__)
login_manager = LoginManager()
migrate = Migrate(app, db)

# App configuration
app.config['SECRET_KEY'] = 'secretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fhData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Components initialization
db.init_app(app)
login_manager.init_app(app)

#Crear las tablas
with app.app_context():
    db.create_all()

# Redirecting to login page and message to not logged in users
login_manager.login_view = 'home'
login_manager.login_message = 'You need to be logged in to access this page'

# Global variables
income_choices = [('Salary', 'Salary'), 
                  ('Investment', 'Investment'),
                  ('Bonus', 'Bonus'), 
                  ('Other', 'Other')]

outcome_choices = [('Food', 'Food'),
                   ('Transport', 'Transport'), 
                   ('Health', 'Health'), 
                   ('Education', 'Education'), 
                   ('Entertainment', 'Entertainment'),
                   ('Other', 'Other')]

# loading user from database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    
    # Setting the forms to send to the modals
    income_form = TransactionForm()
    income_form.type.choices = income_choices

    outcome_form = TransactionForm()
    outcome_form.type.choices = outcome_choices

    if request.method == "POST":
        if income_form.validate_on_submit():
            add_income(income_form)
            return redirect(url_for('logged_in', username=username))
        
        elif outcome_form.validate_on_submit():
            add_outcome(outcome_form)
            return redirect(url_for('logged_in', username=username))

        else: 
            flash('Faild to complete, check inputs', 'error')
            return redirect(url_for('logged_in', username=username))

    
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    outcomes = Outcome.query.filter_by(user_id=current_user.id).all()

    total_income = sum([income.amount for income in incomes])
    total_outcome = sum([outcome.amount for outcome in outcomes])

    # Creating the figure to show the income vs outcome
    ## Setting the grid style of the plot
    sns.set_style('whitegrid')

    ## Creating the figure and the axis (barplot)
    fig = plt.figure(figsize=(10, 5))
    ax = sns.barplot(
        x=['Income', 'Outcome'], 
        y=[total_income, total_outcome], 
        palette=['green', 'red'],
        width=0.3  # Ancho de las barras
    )

    # Add the values to the bars to show the total income and outcome on top of the bars
    for bar, value in zip(ax.patches, [total_income, total_outcome]):
        ax.text(  
            bar.get_x() + bar.get_width() / 2,   
            bar.get_height(), 
            f' {value}',                         # Texto a mostrar
            ha='center',                         # Alineación horizontal
            va='bottom'                          # Alineación vertical
        )

    # Seting the title and labels
    plt.title('Income vs Outcome')
    plt.ylabel('Amount ($)')

    # Saving the plot
    plt.savefig('static/plot.png')
    plt.close(fig)

    return render_template('logged_in.html', 
                           user=current_user, 
                           total_income=total_income, 
                           total_outcome=total_outcome, 
                           plot_url=url_for('static', filename='plot.png'),
                           income_form=income_form,
                           outcome_form=outcome_form
                           )


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
    
    edit_form = EditUserForm(
        username=current_user.username, 
        name=current_user.name
        )

    if edit_form.validate_on_submit():
        current_user.username = edit_form.username.data
        current_user.name = edit_form.name.data

        # Verifying if the user has changed the username, name or password
        if current_user.username:
            current_user.username = edit_form.username.data
        if current_user.name:
            current_user.name = edit_form.name.data
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('logged_in', username=current_user.username))

    return render_template('edit_user.html', edit_form=edit_form)

@app.route('/delete/<username>', methods=['GET', 'POST'])
@login_required
def delete_user(username):

    delete_form = DeleteUserForm()
    user_to_delete = User.query.filter_by(username=username).first()

    if not user_to_delete:
        flash('User not found', 'error')
        return redirect(url_for('home'))

    if delete_form.validate_on_submit():
        
        # Identificar el botón presionado
        action = request.form.get('action')
        
        if action == 'cancel':
            return redirect(url_for('logged_in', username=current_user.username))
        
        elif action == 'delete':
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User deleted successfully', 'success')
            return redirect(url_for('home'))
        
    return render_template('delete_user.html', user=user_to_delete, form=delete_form)

## -- Next comented becouse modal was added to logged_in endpoint --
# Route to add an income
# @app.route('/add_income/<username>', methods=['GET', 'POST'])
# @login_required
def add_income(income_form):
        
    new_income = Income(
        user_id = current_user.id,
        amount = income_form.amount.data,
        type = income_form.type.data,
        description = income_form.description.data
        )
        
    db.session.add(new_income)
    db.session.commit()
    flash('Income added successfully', 'success')
    return redirect(url_for('logged_in', username=current_user.username))
      
    # return render_template('add_income.html', form=income_form)

# Route to add an outcome
# @app.route('/add_outcome/<username>', methods=['GET', 'POST'])
# @login_required
def add_outcome(outcome_form):

    new_outcome = Outcome(
        user_id = int(current_user.id),
        amount = outcome_form.amount.data,
        type = outcome_form.type.data,
        description = outcome_form.description.data
        )

    db.session.add(new_outcome)
    db.session.commit()
    flash('Outcome added successfully', 'success')
    return redirect(url_for('logged_in', username=current_user.username))

# Functions to delete and edit incomes
@app.route('/delete_income/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_income(id):
    income_to_delete = Income.query.get(id)
    if not income_to_delete:
        flash('Income not found', 'error')
        return redirect(url_for('logged_in', username=current_user.username))

    db.session.delete(income_to_delete)
    db.session.commit()
    flash('Income deleted successfully', 'success')
    return redirect(url_for('logged_in', username=current_user.username))

@app.route('/edit_income/<int:id>/<transaction_type>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id, transaction_type):
    
    if transaction_type == 'income':
        transaction = Income.query.get(id)

        transaction_form = TransactionForm(
            amount=transaction.amount,
            description=transaction.description
        )

        transaction_form.type.choices = income_choices # income_choices is a global variable defined at the beginning of this script

        if transaction_form.validate_on_submit():
            transaction.amount = transaction_form.amount.data
            transaction.type = transaction_form.type.data
            transaction.description = transaction_form.description.data

            db.session.commit()
            flash('Income updated successfully', 'success')
            return redirect(url_for('logged_in', username=current_user.username))
    
    elif transaction_type == 'outcome':

        transaction = Outcome.query.get(id)

        transaction_form = TransactionForm(
            amount=transaction.amount,
            description=transaction.description
        )
        
        transaction_form.type.choices = outcome_choices # outcome_choices is a global variable defined at the beginning of this script

        if transaction_form.validate_on_submit():
            transaction.amount = transaction_form.amount.data
            transaction.type = transaction_form.type.data
            transaction.description = transaction_form.description.data

            db.session.commit()
            flash('Outcome updated successfully', 'success')
            return redirect(url_for('logged_in', username=current_user.username))

    return render_template('edit_transaction.html', form=transaction_form)


@app.route('/delete_outcome/<int:id>/<transaction_type>', methods=['GET', 'POST'])
@login_required
def delete_transaction(id, transaction_type):
    
    if transaction_type == 'income':
        transaction_to_delete = Income.query.get(id)
        db.session.delete(transaction_to_delete)
        db.session.commit()
        flash('Income deleted successfully', 'success')
        return redirect(url_for('logged_in', username=current_user.username))
    
    elif transaction_type == 'outcome':
        transaction_to_delete = Outcome.query.get(id)
        db.session.delete(transaction_to_delete)
        db.session.commit()
        flash('Outcome deleted successfully', 'success')
        return redirect(url_for('logged_in', username=current_user.username))
    
    return redirect(url_for('logged_in', username=current_user.username))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
