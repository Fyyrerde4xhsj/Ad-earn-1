from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import firebase_config
import firebase_admin
from firebase_admin import auth, db, firestore
import pyrebase
import time
from datetime import datetime, timedelta
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# Initialize Pyrebase
pyrebase_config = firebase_config.get_firebase_config()
pb = pyrebase.initialize_app(pyrebase_config)
auth_pyrebase = pb.auth()
db_firestore = firebase_config.db_firestore

# Authentication required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_page'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or not session['user'].get('admin', False):
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        user = auth_pyrebase.sign_in_with_email_and_password(email, password)
        user_info = auth.get_user(user['localId'])
        
        # Get user data from Firestore
        user_doc = db_firestore.collection('users').document(user['localId']).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            session['user'] = {
                'uid': user['localId'],
                'email': user_info.email,
                'name': user_data.get('name', 'User'),
                'admin': user_data.get('admin', False)
            }
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'User data not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    referral_code = data.get('referral_code', '')
    
    try:
        # Create user in Firebase Auth
        user = auth_pyrebase.create_user_with_email_and_password(email, password)
        
        # Create user document in Firestore
        user_data = {
            'email': email,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'earnings': 0.0,
            'total_earnings': 0.0,
            'ad_views_today': 0,
            'ad_view_time_today': 0,
            'total_ad_views': 0,
            'referral_code': generate_referral_code(),
            'referrals': 0,
            'referral_earnings': 0.0,
            'withdrawn': 0.0,
            'admin': False
        }
        
        db_firestore.collection('users').document(user['localId']).set(user_data)
        
        # Process referral if applicable
        if referral_code:
            process_referral(referral_code, user['localId'])
        
        # Sign in the user
        user_info = auth.get_user(user['localId'])
        session['user'] = {
            'uid': user['localId'],
            'email': user_info.email,
            'name': name,
            'admin': False
        }
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/dashboard')
@login_required
def dashboard():
    user_doc = db_firestore.collection('users').document(session['user']['uid']).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    
    # Check if daily reset is needed
    check_daily_reset(session['user']['uid'], user_data)
    
    return render_template('dashboard.html', user_data=user_data)

@app.route('/ads')
@login_required
def ads_page():
    user_doc = db_firestore.collection('users').document(session['user']['uid']).get()
    user_data = user_doc.to_dict() if user_doc.exists else {}
    return render_template('ads.html', user_data=user_data)

@app.route('/start_ad', methods=['POST'])
@login_required
def start_ad():
    user_uid = session['user']['uid']
    user_doc = db_firestore.collection('users').document(user_uid).get()
    user_data = user_doc.to_dict()
    
    # Check if user has reached daily limit
    if user_data.get('ad_views_today', 0) >= 10:  # 10 ads * ₹0.11 = ₹1.10
        return jsonify({'success': False, 'message': 'Daily limit reached'})
    
    # Check if user has watched minimum time (5 minutes)
    if user_data.get('total_ad_views', 0) < 10 and user_data.get('ad_view_time_today', 0) < 300:
        return jsonify({'success': False, 'message': 'Watch at least 5 minutes of ads today to unlock earnings'})
    
    # Start ad timer
    ad_data = {
        'start_time': datetime.now().isoformat(),
        'user_uid': user_uid,
        'status': 'started'
    }
    
    db_firestore.collection('ads').document().set(ad_data)
    
    return jsonify({'success': True, 'message': 'Ad started', 'timer': 15})

@app.route('/complete_ad', methods=['POST'])
@login_required
def complete_ad():
    user_uid = session['user']['uid']
    data = request.json
    ad_id = data.get('ad_id')
    
    # Update ad status
    db_firestore.collection('ads').document(ad_id).update({
        'status': 'completed',
        'end_time': datetime.now().isoformat()
    })
    
    # Update user earnings and ad views
    user_ref = db_firestore.collection('users').document(user_uid)
    user_doc = user_ref.get()
    user_data = user_doc.to_dict()
    
    new_earnings = user_data.get('earnings', 0) + 0.11
    new_total_earnings = user_data.get('total_earnings', 0) + 0.11
    new_ad_views_today = user_data.get('ad_views_today', 0) + 1
    new_total_ad_views = user_data.get('total_ad_views', 0) + 1
    
    user_ref.update({
        'earnings': new_earnings,
        'total_earnings': new_total_earnings,
        'ad_views_today': new_ad_views_today,
        'total_ad_views': new_total_ad_views,
        'last_ad_view': datetime.now().isoformat()
    })
    
    return jsonify({
        'success': True, 
        'message': 'Ad completed', 
        'earnings': new_earnings,
        'ad_views_today': new_ad_views_today
    })

@app.route('/blog/<int:blog_id>')
@login_required
def blog_page(blog_id):
    if blog_id < 1 or blog_id > 10:
        return redirect(url_for('dashboard'))
    
    # In a real application, you would fetch blog content from a database
    blog_content = f"This is content for blog post #{blog_id}. Lorem ipsum dolor sit amet..."
    
    return render_template('blog.html', blog_id=blog_id, blog_content=blog_content)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    user_uid = session['user']['uid']
    user_ref = db_firestore.collection('users').document(user_uid)
    user_doc = user_ref.get()
    user_data = user_doc.to_dict()
    
    if request.method == 'POST':
        data = request.json
        upi_id = data.get('upi_id')
        amount = float(data.get('amount', 0))
        
        # Validation
        if amount < 5 or amount > 10:
            return jsonify({'success': False, 'message': 'Amount must be between ₹5 and ₹10'})
        
        if user_data.get('earnings', 0) < amount:
            return jsonify({'success': False, 'message': 'Insufficient balance'})
        
        if user_data.get('total_ad_views', 0) < 10:
            return jsonify({'success': False, 'message': 'Watch at least 10 ads to unlock withdrawals'})
        
        # Create withdrawal request
        withdrawal_data = {
            'user_uid': user_uid,
            'upi_id': upi_id,
            'amount': amount,
            'status': 'pending',
            'requested_at': datetime.now().isoformat(),
            'user_email': user_data.get('email'),
            'user_name': user_data.get('name')
        }
        
        db_firestore.collection('withdrawals').document().set(withdrawal_data)
        
        # Update user balance
        new_balance = user_data.get('earnings', 0) - amount
        total_withdrawn = user_data.get('withdrawn', 0) + amount
        user_ref.update({
            'earnings': new_balance,
            'withdrawn': total_withdrawn
        })
        
        # Send email notification to admin
        send_withdrawal_email(user_data.get('name'), upi_id, amount)
        
        return jsonify({'success': True, 'message': 'Withdrawal request submitted'})
    
    return render_template('withdraw.html', user_data=user_data)

@app.route('/admin')
@admin_required
def admin_panel():
    # Get all users
    users = []
    users_ref = db_firestore.collection('users').stream()
    for user in users_ref:
        user_data = user.to_dict()
        user_data['id'] = user.id
        users.append(user_data)
    
    # Get all withdrawals
    withdrawals = []
    withdrawals_ref = db_firestore.collection('withdrawals').stream()
    for withdrawal in withdrawals_ref:
        withdrawal_data = withdrawal.to_dict()
        withdrawal_data['id'] = withdrawal.id
        withdrawals.append(withdrawal_data)
    
    return render_template('admin.html', users=users, withdrawals=withdrawals)

@app.route('/update_withdrawal_status', methods=['POST'])
@admin_required
def update_withdrawal_status():
    data = request.json
    withdrawal_id = data.get('withdrawal_id')
    status = data.get('status')
    
    db_firestore.collection('withdrawals').document(withdrawal_id).update({
        'status': status,
        'processed_at': datetime.now().isoformat() if status != 'pending' else None
    })
    
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Helper functions
def generate_referral_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def process_referral(referral_code, new_user_uid):
    # Find user with this referral code
    users_ref = db_firestore.collection('users')
    query = users_ref.where('referral_code', '==', referral_code).stream()
    
    for user in query:
        referrer_uid = user.id
        referrer_data = user.to_dict()
        
        # Update referrer's stats
        db_firestore.collection('users').document(referrer_uid).update({
            'referrals': referrer_data.get('referrals', 0) + 1,
            'referral_earnings': referrer_data.get('referral_earnings', 0) + 0.10,
            'earnings': referrer_data.get('earnings', 0) + 0.10,
            'total_earnings': referrer_data.get('total_earnings', 0) + 0.10
        })
        
        # Record the referral
        referral_data = {
            'referrer_uid': referrer_uid,
            'referred_uid': new_user_uid,
            'referral_code': referral_code,
            'date': datetime.now().isoformat()
        }
        db_firestore.collection('referrals').document().set(referral_data)
        
        break

def check_daily_reset(user_uid, user_data):
    last_reset = user_data.get('last_daily_reset')
    if not last_reset or datetime.now().date() > datetime.fromisoformat(last_reset).date():
        db_firestore.collection('users').document(user_uid).update({
            'ad_views_today': 0,
            'ad_view_time_today': 0,
            'last_daily_reset': datetime.now().isoformat()
        })

def send_withdrawal_email(user_name, upi_id, amount):
    # In a real application, you would integrate with an email service
    # For now, we'll just print to console
    print(f"Withdrawal request from {user_name} for ₹{amount} to UPI ID: {upi_id}")
    # Send email to ankurboro236@gmail.com
    # Implementation depends on your email service (SendGrid, SMTP, etc.)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)