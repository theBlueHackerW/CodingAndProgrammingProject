from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_BINDS'] = {'transactions': 'sqlite:///transactions.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    security_code = db.Column(db.String(4), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    __bind_key__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    transaction_type = db.Column(db.String(10))  # 'income' or 'expense'
    recurrence = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    query = request.args.get('q', '')
    transactions_query = Transaction.query.filter_by(username=user.username)
    if query:
        transactions_query = transactions_query.filter(
            (Transaction.category.ilike(f"%{query}%")) | 
            (Transaction.description.ilike(f"%{query}%"))
        )
    transactions = transactions_query.all()
    return render_template('dashboard.html', user=user, transactions=transactions, search_query=query)

@app.route('/graph_data')
def graph_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(session['user_id'])
    transactions = Transaction.query.filter_by(username=user.username).all()
    
    income_total = sum(tx.amount for tx in transactions if tx.transaction_type == "income")
    expense_total = sum(abs(tx.amount) for tx in transactions if tx.transaction_type == "expense")

    category_totals = {}
    for tx in transactions:
        if tx.transaction_type == "expense":
            category_totals[tx.category] = category_totals.get(tx.category, 0) + abs(tx.amount)

    return jsonify({
        "income_vs_expense": {"income": income_total, "expenses": expense_total},
        "category_distribution": category_totals
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        engine = db.get_engine(app, bind='transactions')
        Transaction.metadata.create_all(engine)
    app.run(debug=True)
