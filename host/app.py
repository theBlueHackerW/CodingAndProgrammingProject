from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import plotly.express as px

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
    # Instead of a foreign key, we store the username as a string.
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

# The dashboard route now handles both GET and POST (for report generation)
@app.route('/dashboard', methods=['GET', 'POST'])
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

    # Initialize report variables
    report_graph = None
    report_summary = ""
    report_stats = ""
    selected_graph = None
    selected_period = None

    # If the report form was submitted via POST, generate the graph and statistics
    if request.method == 'POST':
        graph_type = request.form.get('graph_type')
        period = request.form.get('period')
        selected_graph = graph_type
        selected_period = period

        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - pd.Timedelta(days=7)
        elif period == "month":
            start_date = end_date - pd.Timedelta(days=30)
        elif period == "year":
            start_date = end_date - pd.Timedelta(days=365)
        else:  # "all" or unspecified
            start_date = None

        report_query = Transaction.query.filter_by(username=user.username)
        if start_date:
            report_query = report_query.filter(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        report_transactions = report_query.all()

        if report_transactions:
            data = {
                "date": [tx.transaction_date for tx in report_transactions],
                "amount": [tx.amount for tx in report_transactions],
                "transaction_type": [tx.transaction_type for tx in report_transactions],
                "category": [tx.category for tx in report_transactions]
            }
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(columns=["date", "amount", "transaction_type", "category"])

        # Generate graph and statistics based on the selected graph type
        if graph_type == "balance_time":
            df_sorted = df.sort_values("date")
            if not df_sorted.empty:
                computed_balance = df_sorted["amount"].cumsum()
                offset = user.balance - computed_balance.iloc[-1]
                df_sorted["actual_balance"] = computed_balance + offset
                fig = px.line(df_sorted, x="date", y="actual_balance", title="Account Balance Over Time")
                initial = df_sorted["actual_balance"].iloc[0]
                final = df_sorted["actual_balance"].iloc[-1]
                report_summary = f"Your account balance changed from ${initial:.2f} to ${final:.2f} over the selected period."
                avg_daily_change = df_sorted["actual_balance"].diff().mean()
                max_balance = df_sorted["actual_balance"].max()
                min_balance = df_sorted["actual_balance"].min()
                stats_list = [
                    f"Average daily change: ${avg_daily_change:.2f}",
                    f"Highest balance: ${max_balance:.2f}",
                    f"Lowest balance: ${min_balance:.2f}"
                ]
                report_stats = "<br>".join(stats_list)
            else:
                fig = px.line(title="Account Balance Over Time")
                report_summary = "No transactions available for the selected period."
                report_stats = "No statistics available."
        elif graph_type == "income_expenses_time":
            df_income = df[df["transaction_type"] == "income"].sort_values("date")
            df_expense = df[df["transaction_type"] == "expense"].sort_values("date")
            fig = px.line(title="Income and Expenses Over Time")
            if not df_income.empty:
                fig.add_scatter(x=df_income["date"], y=df_income["amount"], mode="lines+markers", name="Income")
            if not df_expense.empty:
                fig.add_scatter(x=df_expense["date"], y=df_expense["amount"], mode="lines+markers", name="Expenses")
            report_summary = "This graph shows your income and expenses over the selected period."
            avg_income = df_income["amount"].mean() if not df_income.empty else 0
            avg_expense = df_expense["amount"].mean() if not df_expense.empty else 0
            total_income = df_income["amount"].sum() if not df_income.empty else 0
            total_expense = abs(df_expense["amount"].sum()) if not df_expense.empty else 0
            stats_list = [
                f"Average income: ${avg_income:.2f}",
                f"Total income: ${total_income:.2f}",
                f"Average expense: ${avg_expense:.2f}",
                f"Total expenses: ${total_expense:.2f}"
            ]
            report_stats = "<br>".join(stats_list)
        elif graph_type == "bar_category_income":
            df_income = df[df["transaction_type"] == "income"]
            df_grouped = df_income.groupby("category")["amount"].sum().reset_index()
            fig = px.bar(df_grouped, x="category", y="amount", title="Total Income by Category")
            report_summary = "The bar graph displays your total income grouped by category."
            if not df_grouped.empty:
                top_category = df_grouped.loc[df_grouped["amount"].idxmax()]
                report_stats = f"Top income category: {top_category['category']} with total of ${top_category['amount']:.2f}."
            else:
                report_stats = "No statistics available."
        elif graph_type == "bar_category_expense":
            df_expense = df[df["transaction_type"] == "expense"]
            df_expense = df_expense.copy()
            df_expense["amount"] = df_expense["amount"].abs()
            df_grouped = df_expense.groupby("category")["amount"].sum().reset_index()
            fig = px.bar(df_grouped, x="category", y="amount", title="Total Expenses by Category")
            report_summary = "The bar graph displays your total expenses grouped by category."
            if not df_grouped.empty:
                top_category = df_grouped.loc[df_grouped["amount"].idxmax()]
                report_stats = f"Top expense category: {top_category['category']} with total of ${top_category['amount']:.2f}."
            else:
                report_stats = "No statistics available."
        elif graph_type == "pie_category_income":
            df_income = df[df["transaction_type"] == "income"]
            df_grouped = df_income.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(df_grouped, names="category", values="amount", title="Income Distribution by Category")
            report_summary = "The pie chart shows the proportion of total income by category."
            if not df_grouped.empty:
                top_category = df_grouped.loc[df_grouped["amount"].idxmax()]
                report_stats = f"Highest income share: {top_category['category']} with ${top_category['amount']:.2f}."
            else:
                report_stats = "No statistics available."
        elif graph_type == "pie_category_expense":
            df_expense = df[df["transaction_type"] == "expense"]
            df_expense = df_expense.copy()
            df_expense["amount"] = df_expense["amount"].abs()
            df_grouped = df_expense.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(df_grouped, names="category", values="amount", title="Expenses Distribution by Category")
            report_summary = "The pie chart shows the proportion of total expenses by category."
            if not df_grouped.empty:
                top_category = df_grouped.loc[df_grouped["amount"].idxmax()]
                report_stats = f"Highest expense share: {top_category['category']} with ${top_category['amount']:.2f}."
            else:
                report_stats = "No statistics available."
        elif graph_type == "pie_income_vs_expenses":
            total_income = df[df["transaction_type"] == "income"]["amount"].sum()
            total_expense = abs(df[df["transaction_type"] == "expense"]["amount"].sum())
            fig = px.pie(names=["Income", "Expenses"], values=[total_income, total_expense], title="Income vs. Expenses")
            report_summary = "This pie chart compares your total income to your total expenses over the selected period."
            if total_income + total_expense > 0:
                perc_income = (total_income / (total_income + total_expense)) * 100
                perc_expense = (total_expense / (total_income + total_expense)) * 100
                report_stats = f"Income: {perc_income:.1f}%<br>Expenses: {perc_expense:.1f}%"
            else:
                report_stats = "No statistics available."
        else:
            fig = px.line(title="No Graph Selected")
            report_summary = "No valid graph type was selected."
            report_stats = "No statistics available."

        report_graph = fig.to_html(full_html=False)

    return render_template('dashboard.html', user=user, transactions=transactions, search_query=query,
                           report_graph=report_graph, report_summary=report_summary, report_stats=report_stats,
                           selected_graph=selected_graph, selected_period=selected_period)

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

@app.route('/graph_data', methods=['POST'])
def graph_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(session['user_id'])

    transactions = Transaction.query.filter_by(username=user.username).all()
    
    income_total = sum(tx.amount for tx in transactions if tx.transaction_type == "income")
    expense_total = sum(abs(tx.amount) for tx in transactions if tx.transaction_type == "expense")

    category_totals = {}
    for tx in transactions:
        if tx.transaction_type == "expense":  # Only track expenses
            category_totals[tx.category] = category_totals.get(tx.category, 0) + abs(tx.amount)

    return jsonify({
        "income_vs_expense": {"income": income_total, "expenses": expense_total},
        "category_distribution": category_totals
    })

# -----------------------------
# Create databases if they don't exist
# -----------------------------
with app.app_context():
    db.create_all()  # Creates tables for accounts.db
    engine = db.get_engine(app, bind='transactions')
    Transaction.metadata.create_all(engine)

if __name__ == "__main__":
    app.run(debug=True)
