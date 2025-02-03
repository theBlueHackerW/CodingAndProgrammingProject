# FinanceEase

## Overview
FinanceEase is a personal finance management web application that allows users to track their income and expenses, generate financial reports, and maintain a clear record of their transactions. Built with Flask and SQLite, the application provides an intuitive dashboard for monitoring financial activity.

## Features
- **User Authentication:** Secure user registration and login with a 4-digit security code.
- **Account Management:** Users can update their account balance and track financial activity.
- **Transaction Tracking:** Add, edit, and delete income and expense transactions with categorized labels.
- **Financial Reports:** Generate visual reports, including line graphs, bar charts, and pie charts for income, expenses, and overall balance.
- **Data Visualization:** Uses Plotly and Chart.js for interactive and insightful graphical representations.
- **Search & Filtering:** Find transactions easily by searching through categories or descriptions.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- pip (Python package manager)
- Virtual environment (optional but recommended)

### Setup Instructions
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/FinanceEase.git
   cd FinanceEase
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database:**
   ```python
   from app import db, app
   with app.app_context():
       db.create_all()
   ```

5. **Run the Application:**
   ```bash
   python app.py
   ```

6. Open a browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Usage
1. **Register an Account** – Create an account with a username, email, password, and security code.
2. **Login** – Use your credentials and security code to access the dashboard.
3. **Update Balance** – Set your initial account balance.
4. **Manage Transactions** – Add income and expense transactions categorized for better organization.
5. **Generate Reports** – Select time periods and visualization types to analyze financial trends.
6. **Search Transactions** – Use keywords to find specific financial entries.

## Technologies Used
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Jinja2
- **Visualization:** Plotly, Chart.js
- **Authentication & Security:** Flask-Session, Flask-Flash

## File Structure
```
/FinanceEase
│-- app.py               # Main Flask application
│-- dashboard.html       # HTML template for dashboard
│-- templates/           # Folder for Jinja2 HTML templates
│-- static/              # Static assets (CSS, JS)
│-- accounts.db          # SQLite database for user accounts
│-- transactions.db      # SQLite database for transactions
│-- requirements.txt     # Python dependencies
│-- README.md            # Project documentation (this file)
```

## Future Enhancements
- Implement password hashing for secure authentication.
- Add multi-user support with different financial goals.
- Export transaction reports in CSV or PDF format.
- Integrate with external bank APIs for real-time data synchronization.

## License
No license specified. Please define the licensing terms for this project.

---

Let me know if you need modifications or additional details! 🚀
