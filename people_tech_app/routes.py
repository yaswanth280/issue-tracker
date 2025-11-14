# routes.py
from app import app
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Issue, Response, db
from datetime import datetime

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    issues = Issue.query.filter_by(user_id=current_user.id).order_by(Issue.created_at.desc()).all()
    return render_template('dashboard.html', issues=issues)

@app.route('/raise_issue', methods=['GET', 'POST'])
@login_required
def raise_issue():
    if current_user.is_admin:
        flash('Admins cannot raise issues.')
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        issue = Issue(title=title, description=description, category=category, user_id=current_user.id)
        db.session.add(issue)
        db.session.commit()
        flash('Issue raised successfully!')
        return redirect(url_for('dashboard'))
    return render_template('raise_issue.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    issues = Issue.query.order_by(Issue.created_at.desc()).all()
    return render_template('admin_dashboard.html', issues=issues)

@app.route('/respond/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def respond(issue_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    issue = Issue.query.get_or_404(issue_id)
    if request.method == 'POST':
        content = request.form['content']
        response = Response(content=content, issue_id=issue_id, admin_id=current_user.id)
        issue.status = 'Responded'
        db.session.add(response)
        db.session.commit()
        flash('Response sent!')
        return redirect(url_for('admin_dashboard'))
    responses = Response.query.filter_by(issue_id=issue_id).all()
    return render_template('respond.html', issue=issue, responses=responses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/view_issue/<int:issue_id>')
@login_required
def view_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if issue.user_id != current_user.id:
        flash('Access denied.')
        return redirect(url_for('dashboard'))
    
    responses = Response.query.filter_by(issue_id=issue_id).order_by(Response.created_at).all()
    return render_template('view_issue.html', issue=issue, responses=responses)