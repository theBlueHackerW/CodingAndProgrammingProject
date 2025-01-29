from app import app, db

with app.app_context():
    db.create_all()  # This will create the test.db file and the User table
