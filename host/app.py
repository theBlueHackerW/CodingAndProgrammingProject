from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

# Initialize Flask app
app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a model for user accounts
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(6), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Create Account route
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Handle form submission logic
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        # Generate a unique 6-digit account number
        account_number = str(random.randint(100000, 999999))
        while User.query.filter_by(account_number=account_number).first() is not None:
            account_number = str(random.randint(100000, 999999))
        
        # Save user to the database
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
            account_number=account_number
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))

    # Render the Create Account page
    return render_template('createAccount.html')

# Create database if not exists
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
