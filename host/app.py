from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Main database for user accounts (accounts.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
# Additional bind for transactions (transactions.db)
app.config['SQLALCHEMY_BINDS'] = {
    'transactions': 'sqlite:///transactions.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# Models
# -----------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(50), nullable=False)
    last_name    = db.Column(db.String(50), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    password     = db.Column(db.String(100), nullable=False)
    security_code= db.Column(db.String(4), nullable=False)  # 4-digit security code
    balance      = db.Column(db.Float, default=0.0)  # Default balance is 0

    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    __bind_key__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    # Instead of a foreign key to User, we store the username as a string.
    username = db.Column(db.String(80), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    transaction_type = db.Column(db.String(10))  # 'income' or 'expense'
    recurrence = db.Column(db.Integer, default=0)  # 0 = one-time; otherwise recurring (in days)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Transaction {self.id} {self.transaction_type} {self.amount}>'

# -----------------------------
# Routes
# -----------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        first_name    = request.form['firstName']
        last_name     = request.form['lastName']
        email         = request.form['email']
        username      = request.form['username']
        password      = request.form['password']
        security_code = request.form['securityCode']

        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "error")
            return render_template("createAccount.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please use a different email.", "error")
            return render_template("createAccount.html")

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            security_code=security_code
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("createAccount.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username      = request.form['username']
        security_code = request.form['account_code']  # The login form uses this field name
        password      = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.security_code == security_code:
                session['user_id'] = user.id
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid security code.", "error")
        else:
            flash("Invalid username or password.", "error")
        return render_template("login.html")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    query = request.args.get('q', '')
    # Query transactions by username (stored in transactions.db)
    transactions_query = Transaction.query.filter_by(username=user.username)
    if query:
        transactions_query = transactions_query.filter(
            (Transaction.category.ilike(f"%{query}%")) | 
            (Transaction.description.ilike(f"%{query}%"))
        )
    transactions = transactions_query.all()
    return render_template('dashboard.html', user=user, transactions=transactions, search_query=query)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    try:
        new_balance = float(request.form.get('balance'))
        user.balance = new_balance
        db.session.commit()
        flash("Account balance updated.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to update balance.", "error")
    return redirect(url_for('dashboard'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    try:
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        transaction_type = request.form.get('transaction_type')  # "income" or "expense"
        recurrence = int(request.form.get('recurrence', 0))
        description = request.form.get('description')
        # Ensure the amount is positive for income and negative for expense.
        if transaction_type == "expense":
            amount = -abs(amount)
        else:
            amount = abs(amount)
        new_tx = Transaction(
            username=user.username,
            amount=amount,
            category=category,
            transaction_type=transaction_type,
            recurrence=recurrence,
            description=description
        )
        db.session.add(new_tx)
        user.balance += amount
        db.session.commit()
        flash("Transaction added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error adding transaction.", "error")
    return redirect(url_for('dashboard'))

@app.route('/edit_transaction/<int:tx_id>', methods=['POST'])
def edit_transaction(tx_id):
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    tx = Transaction.query.get(tx_id)
    if tx.username != user.username:
        flash("Not authorized.", "error")
        return redirect(url_for('dashboard'))
    try:
        new_amount = float(request.form.get('amount'))
        new_category = request.form.get('category')
        new_type = request.form.get('transaction_type')
        new_recurrence = int(request.form.get('recurrence', 0))
        new_description = request.form.get('description')
        if new_type == "expense":
            new_amount = -abs(new_amount)
        else:
            new_amount = abs(new_amount)
        old_amount = tx.amount
        tx.amount = new_amount
        tx.category = new_category
        tx.transaction_type = new_type
        tx.recurrence = new_recurrence
        tx.description = new_description
        user.balance = user.balance - old_amount + new_amount
        db.session.commit()
        flash("Transaction updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating transaction.", "error")
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<int:tx_id>', methods=['POST'])
def delete_transaction(tx_id):
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    tx = Transaction.query.get(tx_id)
    if tx.username != user.username:
        flash("Not authorized.", "error")
        return redirect(url_for('dashboard'))
    try:
        user.balance -= tx.amount
        db.session.delete(tx)
        db.session.commit()
        flash("Transaction deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting transaction.", "error")
    return redirect(url_for('dashboard'))

@app.route('/check_user', methods=['POST'])
def check_user():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    
    errors = {}
    if username and User.query.filter_by(username=username).first():
        errors['username'] = "Username already exists."
    if email and User.query.filter_by(email=email).first():
        errors['email'] = "Email already registered."
    
    return jsonify({"errors": errors}), 200

# -----------------------------
# Create databases if they don't exist
# -----------------------------
with app.app_context():
    db.create_all()  # Creates tables for accounts.db
    engine = db.get_engine(app, bind='transactions')
    Transaction.metadata.create_all(engine)

if __name__ == "__main__":
    app.run(debug=True)
