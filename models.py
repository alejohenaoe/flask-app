from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(
        Enum('Salary', 'Investment', 'Bonus', 'Other', name='income_types'), 
        nullable=False, 
        index=True
        )
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    
    user = db.relationship('User', backref=db.backref('incomes', lazy=True))

class Outcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(
        Enum('Food', 'Transport', 'Health', 'Education', 'Entertainment', 'Other', name='outcome_type'), 
        nullable=False, 
        index=True
        )
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    
    user = db.relationship('User', backref=db.backref('outcomes', lazy=True))