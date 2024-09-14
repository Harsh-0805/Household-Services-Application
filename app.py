from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from extensions import db  # Import db from the extensions file
from models import User, Service, ServiceRequest  # Import models here

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize the database with the app
db.init_app(app)

# Initialize the login manager with the app
login_manager = LoginManager()
login_manager.init_app(app)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for login, register, and logout
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'professional':
                return redirect(url_for('service_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    services = Service.query.all()
    return render_template('dashboard_admin.html', services=services)

@app.route('/service_dashboard')
@login_required
def service_dashboard():
    if current_user.role != 'professional':
        return redirect(url_for('index'))
    service_requests = ServiceRequest.query.filter_by(professional_id=current_user.id).all()
    return render_template('dashboard_service.html', requests=service_requests)

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    services = Service.query.all()
    return render_template('dashboard_customer.html', services=services)

if __name__ == '__main__':
    # Run the application and create tables if they don't exist
    with app.app_context():
        db.create_all()  # Create the tables for the database

        # Optionally, you can add some initial data here
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('adminpassword')
            db.session.add(admin)

        if not Service.query.filter_by(name='AC Repair').first():
            service1 = Service(name='AC Repair', description='Air conditioner repair service', price=200.0)
            db.session.add(service1)

        db.session.commit()

    app.run(debug=True)
