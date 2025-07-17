from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
import csv, os, hashlib, shutil, random, string, time, smtplib, ssl

app = Flask(__name__)
app.secret_key = '123456789'

# Configuration for email sending
EMAIL_ADDRESS = "llaka2937@gmail.com"
EMAIL_PASSWORD = "hqim uqwh qlkb jpde"  # Use app password if 2FA is enabled

LOGIN_FILE = 'login_data.csv'
SETTING_FILE = 'user_setting.csv'
USER_FOLDER = 'users'
UPLOAD_LIMIT_MB = 2

if not os.path.exists(USER_FOLDER):
    os.makedirs(USER_FOLDER, exist_ok=True)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def read_users():
    if not os.path.exists(LOGIN_FILE):
        return []
    with open(LOGIN_FILE, newline='') as f:
        return list(csv.DictReader(f))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'json' , 'txt', 'py', 'html', 'css', 'js', 'md' , 'jpg', 'jpeg', 'png'}

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_otp_email(receiver_email, otp):
    subject = "🔐 Your Haradi Bots OTP Code"
    sender_name = "Haradi Bots"

    # Plain text fallback
    text_body = f"""Hello,

Your One-Time Password (OTP) is: {otp}

Enter this to complete your signup.

If you didn't request this, please ignore.

– Haradi Bots Team
"""

    # HTML email body
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50;">Welcome to <span style="color: #2980b9;">Haradi Bots</span> 🤖</h2>
          <p style="font-size: 16px;">Your <strong style="color: #2ecc71;">One-Time Password (OTP)</strong> is:</p>
          <div style="font-size: 28px; font-weight: bold; margin: 15px 0; color: #e74c3c;">{otp}</div>
          <p style="font-size: 14px;">Please use this OTP to verify your email and complete the signup process. The code will expire in 5 minutes.</p>
          <hr style="margin: 20px 0;">
          <p style="font-size: 12px; color: #7f8c8d;">Didn't request this email? Just ignore it.</p>
          <p style="font-size: 12px; color: #7f8c8d;">– Haradi Bots Team</p>
        </div>
      </body>
    </html>
    """

    # Compose message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{sender_name} <{EMAIL_ADDRESS}>"
    message["To"] = receiver_email

    # Attach both versions
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    # Send via secure Gmail SMTP
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, message.as_string())


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# ------------------ Routes ------------------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        email = request.form['email'].strip().lower()

        users = read_users()

        # ✅ Check if username or email already exists
        for user in users:
            if user['username'].lower() == username.lower():
                flash("Username already exists. Please choose another one.")
                return redirect('/signup')
            if 'email' in user and user['email'].lower() == email:
                flash("Email already registered. Try logging in or use a different email.")
                return redirect('/signup')

        # ✅ Store temporarily in session for verification
        session['temp_username'] = username
        session['temp_password'] = hash_password(password)
        session['temp_email'] = email

        # ✅ Generate and send OTP
        otp = generate_otp()
        session['otp'] = otp
        session['otp_time'] = time.time()

        try:
            send_otp_email(email, otp)
            flash("OTP sent to your email. Please verify.")
            return redirect('/verify')
        except Exception as e:
            flash(f"Failed to send OTP: {e}")
            return redirect('/signup')

    return render_template('signup.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        original_otp = session.get('otp')
        otp_time = session.get('otp_time')

        if time.time() - session.get('otp_time', 0) > 300:
            flash("OTP expired. Please sign up again.")
            return redirect('/signup')

        if entered_otp != original_otp:
            flash("Invalid OTP. Please try again.")
            return redirect('/verify')

        # Create the user account
        username = session.pop('temp_username')
        password = session.pop('temp_password')
        email = session.pop('temp_email')

        users = read_users()

        # Assign a unique user_id
        existing_ids = [int(u['user_id']) for u in users if u['user_id'].isdigit()]
        new_id = str(max(existing_ids) + 1 if existing_ids else 1)

        # Save user to CSV with email
        with open(LOGIN_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(['user_id', 'username', 'email', 'password'])
            writer.writerow([new_id, username,email, password ])

        # Save default user settings
        with open(SETTING_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(['user_id', 'theme', 'editor_font'])
            writer.writerow([new_id, '', ''])

        # Create user folder safely
        user_folder = os.path.join(USER_FOLDER, new_id)
        os.makedirs(user_folder, exist_ok=True)

        flash("Signup complete. Please login.")
        return redirect('/login')

    return render_template('verify.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        raw_password = request.form.get('password', '')

        if not username or not raw_password:
            flash("Please enter both username and password.")
            return redirect('/login')

        try:
            users = read_users()
        except Exception as e:
            flash(f"Server error while reading user data. Try again later.")
            return redirect('/login')

        # Find the user by username (case-insensitive)
        matched_user = next((u for u in users if u['username'].lower() == username.lower()), None)

        if not matched_user:
            flash("Username not found.")
            return redirect('/login')

        hashed_input_password = hash_password(raw_password)
        if matched_user['password'] != hashed_input_password:
            flash("Incorrect password.")
            return redirect('/login')

        # Login successful
        session['user_id'] = matched_user['user_id']
        session['username'] = matched_user['username']
        return redirect('/dashboard')

    return render_template('login.html')

# ------------------ Forgot Password ------------------

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        users = read_users()
        user = next((u for u in users if u.get('email') == email), None)

        if user:
            otp = generate_otp()
            session['reset_email'] = email
            session['reset_otp'] = otp
            session['reset_time'] = time.time()
            send_otp_email(email, otp)
            flash('OTP sent to your email.')
            return redirect('/verify_reset')
        else:
            flash('Email not found.')
    return render_template('forgot_password.html')

@app.route('/verify_reset', methods=['GET', 'POST'])
def verify_reset():
    if request.method == 'POST':
        entered = request.form['otp']
        if time.time() - session.get('reset_time', 0) > 300:
            flash('OTP expired.')
            return redirect('/forgot_password')
        if entered == session.get('reset_otp'):
            return redirect('/reset_password')
        flash('Invalid OTP.')
    return render_template('verify_reset.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_pass = hash_password(request.form['password'])
        email = session.get('reset_email')

        # Update CSV
        users = read_users()
        for u in users:
            if u.get('email') == email:
                u['password'] = new_pass
        with open(LOGIN_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['user_id', 'username', 'email', 'password'])
            writer.writeheader()
            writer.writerows(users)

        flash('Password reset successful.')
        return redirect('/login')
    return render_template('reset_password.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('dashboard.html', username=session['username'])

# ------------------ logout ------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ------------------hosting------------------

@app.route('/hosting')
def hosting():
    return render_template('hosting.html')

# ------------------notebook------------------

@app.route('/notebook')
def notebook():
    return render_template('notebook.html')

# ------------------port------------------

@app.route('/port')
def port():
    return render_template('port.html')

# ------------------supervised learning------------------

@app.route('/supervised')
def supervised():
    return render_template('supervised.html')

# ------------------unsupervised learning------------------

@app.route('/unsupervised')
def unsupervised():
    return render_template('unsupervised.html')

# ------------------reinforcement learning------------------

@app.route('/reinforcement')
def reinforcement():
    return render_template('reinforcement.html')

# ------------------Neural learning------------------

@app.route('/Neural')
def Neural():
    return render_template('Neural.html')


# ------------------Neural learning------------------

@app.route('/deep')
def deep():
    return render_template('deep.html')


# ------------------python for robo ------------------

@app.route('/python_for_robo')
def python_for_robo():
    return render_template('python_for_robo.html')
# ------------------ Project Creation ------------------

# protectin session 

from datetime import timedelta

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

# Optional if you want sessions to expire soon
app.permanent_session_lifetime = timedelta(minutes=45)


# ------------------ Run ------------------

if __name__ == '__main__':
    app.run(debug=True)
