import json
import random
import torch
import torch.nn as nn
import torch.optim as optim
import requests
import re
import os
import math
from collections import Counter, defaultdict
from datetime import datetime
import csv
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify ,send_from_directory
import hashlib
import smtplib
import secrets
from email.message import EmailMessage
from pathlib import Path
from flask_cors import CORS
import threading
from math import ceil
from main import Haradi
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)


# Secure session config
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True  # Set to True with HTTPS
)
config = {
    "EMAIL": "llaka2937@gmail.com",
    "PASSWORD": "hqim uqwh qlkb jpde"
}

# User Management Functions
def ensure_files_exist():
    files = [
        ("./data/users.csv", ["username", "email", "password_hash", "is_verified", "token"]),
        ("user_data.csv", []),
        ("location_log.csv", ["timestamp", "latitude", "longitude", "ip_address"])
    ]
    
    for filename, headers in files:
        if not Path(filename).exists():
            with open(filename, 'w', newline='') as f:
                if headers:
                    writer = csv.writer(f)
                    writer.writerow(headers)

ensure_files_exist()

def send_email(to, subject, content):
    try:
        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = subject
        msg["From"] = config["EMAIL"]
        msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(config["EMAIL"], config["PASSWORD"])
            smtp.send_message(msg)
    except Exception as e:
        print("Email send failed:", e)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(identifier):
    try:
        with open("./data/users.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == identifier or row["email"] == identifier:
                    return row
    except Exception as e:
        print("Error reading CSV:", e)
    return None

def update_user(field, value, identifier):
    rows = []
    updated = False
    with open("./data/users.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == identifier or row["email"] == identifier or row["token"] == identifier:
                row[field] = value
                updated = True
            rows.append(row)
    if updated:
        with open("./data/users.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

def get_login_info():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "Unknown")
    time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return ip, ua, time

# Web Routes
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect("/signup")

        if get_user(username) or get_user(email):
            flash("Username or email already exists.", "error")
            return redirect("/signup")

        if "@" not in email or "." not in email:
            flash("Invalid email address.", "error")
            return redirect("/signup")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect("/signup")

        password_hash = hash_password(password)
        token = secrets.token_urlsafe(32)

        try:
            with open("./data/users.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([username, email, password_hash, "False", token])
            
            
            send_email(email, "Verify Your Account",
                     f"Click here to verify: {request.url_root}verify/{token}")
            flash("Verification email sent. Please check your inbox.", "success")
            return render_template("verify.html", email=email)
        except Exception as e:
            flash("Failed to create account. Try again.", "error")
            print(e)
    return render_template("signup.html")

@app.route("/verify/<token>")
def verify(token):
    user = None
    try:
        with open("./data/users.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["token"] == token:
                    user = row
                    break
        if not user:
            flash("Invalid or expired token.", "error")
            return redirect("/login")
        update_user("is_verified", "True", user["email"])
        flash("Email verified successfully!", "success")
    except Exception as e:
        flash("Error during verification.", "error")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"].strip()
        password = hash_password(request.form["password"])

        user = get_user(identifier)
        if not user:
            flash("User not found.", "error")
            return redirect("/login")
        if user["password_hash"] != password:
            flash("Incorrect password.", "error")
            return redirect("/login")
        if user["is_verified"] != "True":
            flash("Please verify your email before logging in.", "error")
            return redirect("/login")

        session["user"] = user["username"]
        flash("Logged in successfully!", "success")

        ip, ua, time = get_login_info()
        login_msg = f"""
========================================
     SECURITY ALERT: NEW LOGIN DETECTED
========================================

Hello {user['username']},

We noticed a new login to your account.

----------------------------------------
🕒 Time:     {time}
🌐 IP:       {ip}
💻 Device:   {ua}
----------------------------------------

If this was NOT you, please change your password immediately:
https://haradibots.com/reset-password

Stay safe,
Haradi Bots Security Team
========================================
"""

        send_email(user["email"], "Security Alert: New Login Detected", login_msg)

        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("You must be logged in to access the dashboard.", "error")
        return redirect("/login")
    
    username = session["user"]

    
    return render_template("dashboard.html", 
                         user=username)



@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = get_user(email)
        if not user:
            flash("Email not registered.", "error")
            return redirect("/forgot")
        token = secrets.token_urlsafe(32)
        update_user("token", token, email)
        send_email(email, "Reset Password",
                   f"Click to reset: https://haradibots.onrender.com/reset/{token}")
        flash("Reset link sent to your email.", "success")
        return redirect("/login")
    return render_template("forgot.html")

@app.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):
    if request.method == "POST":
        new_password = request.form["password"]
        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(request.url)
        password_hash = hash_password(new_password)
        update_user("password_hash", password_hash, token)
        flash("Password updated successfully!", "success")
        return redirect("/login")
    return render_template("reset.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "success")
    return redirect("/login")

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')

    with open('location_log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), lat, lon, request.remote_addr])

    return {'status': 'success'}, 200

@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    if lat and lon:
        api_key = "2f92ee1b574b4ecca17fefa05f369eca"
        url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={api_key}"
        res = requests.get(url).json()

        if res['results']:
            components = res['results'][0]['components']
            city = components.get('city', components.get('town', ''))
            state = components.get('state', '')
            country = components.get('country', '')

            return jsonify({
                "city": city,
                "state": state,
                "country": country
            })

    return jsonify({"status": "failed"})




# harnidh bot

chatbot = Haradi()  # Initialize chatbot when app starts

@app.route('/Haradi')
def harnidh():
    if "user" not in session:
        flash("You must be logged in to access the page.", "error")
        return redirect("/login")
    
    username = session["user"]

    
    return render_template("Harnidh.html", 
                         user=username)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '').strip()
    response = chatbot.get_response(user_input)
    return jsonify({'response': response})

# lets make routs more and more 


@app.route('/notes')
def notes():
    if "user" not in session:
        flash("You must be logged in to access the page.", "error")
        return redirect("/login")
    
    username = session["user"]
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of notes per page
    notes_data = []
    
    # Path to your CSV file
    csv_path = os.path.join('data', 'notes_data.csv')
    
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Filter notes for current user and public notes
            user_notes = []
            for row in reader:
                if row.get('visibility', 'private') == 'public' or row['author'] == username:
                    if row['author'] == '{{user}}':
                        row['author'] = username
                    user_notes.append(row)
                    
            # Calculate pagination
            total_notes = len(user_notes)
            total_pages = ceil(total_notes / per_page)
            
            # Validate page number
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages
            
            # Get notes for current page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            notes_data = user_notes[start_idx:end_idx]
            
    except FileNotFoundError:
        flash("Notes database not found", "error")
    except Exception as e:
        flash(f"Error loading notes: {str(e)}", "error")
    
    return render_template("notes.html", 
                         user=username,
                         notes=notes_data,
                         page=page,
                         total_pages=total_pages,
                         total_notes=total_notes)

@app.route('/download_note/<int:note_id>')
def download_note(note_id):
    if "user" not in session:
        flash("You must be logged in to download notes.", "error")
        return redirect("/login")
    
    # Find the note in CSV
    csv_path = os.path.join('data', 'notes_data.csv')
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['note_id']) == note_id and row['author'] in (session["user"], '{{user}}'):
                    note_path = row['note_path']
                    # Ensure the path is safe and within allowed directories
                    safe_path = os.path.normpath(note_path)
                    if not safe_path.startswith('static/'):
                        flash("Invalid file path", "error")
                        return redirect("/notes")
                    
                    directory = os.path.dirname(safe_path)
                    filename = os.path.basename(safe_path)
                    
                    # Check if file exists
                    if not os.path.exists(os.path.join(directory, filename)):
                        flash("File not found on server", "error")
                        return redirect("/notes")
                    
                    return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading note: {str(e)}", "error")
    
    flash("Note not found", "error")
    return redirect("/notes")

@app.route('/upload_note', methods=['POST'])
def upload_note():
    if "user" not in session:
        flash("You must be logged in to upload notes.", "error")
        return redirect("/login")
    
    username = session["user"]
    
    try:
        # Get form data
        title = request.form.get('noteTitle')
        tag = request.form.get('noteTag')
        description = request.form.get('noteDescription')
        note_file = request.files.get('noteFile')
        note_image = request.files.get('noteImage')
        visibility = request.form.get('noteVisibility', 'private')  # Default to private if not specified
        
        # Validate required fields
        if not all([title, tag, description, note_file]):
            flash("All required fields must be filled", "error")
            return redirect("/notes")
        
        # Validate file type
        if not note_file.filename.lower().endswith('.pdf'):
            flash("Only PDF files are allowed for notes", "error")
            return redirect("/notes")
        
        # Generate new note ID
        csv_path = os.path.join('data', 'notes_data.csv')
        note_id = 1
        
        # Get existing fieldnames if file exists
        fieldnames = ['note_id', 'title', 'tag', 'note_path', 'note_img_path', 'about_text', 'upload_date', 'author', 'visibility']
        
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                existing_ids = [int(row['note_id']) for row in reader if row['note_id'].isdigit()]
                if existing_ids:
                    note_id = max(existing_ids) + 1
                
                # Update fieldnames from existing file if it has more fields
                if reader.fieldnames:
                    fieldnames = list(reader.fieldnames)
                    if 'visibility' not in fieldnames:
                        fieldnames.append('visibility')
        
        # Save uploaded files
        upload_dir = os.path.join('static', 'uploads', username)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save PDF file
        pdf_filename = f"note_{note_id}.pdf"
        pdf_path = os.path.join(upload_dir, pdf_filename)
        note_file.save(pdf_path)
        
        # Save image if provided
        img_filename = None
        if note_image and note_image.filename:
            img_ext = os.path.splitext(note_image.filename)[1].lower()
            if img_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                img_filename = f"preview_{note_id}{img_ext}"
                img_path = os.path.join(upload_dir, img_filename)
                note_image.save(img_path)
        
        # Add new note to CSV
        new_note = {
            'note_id': str(note_id),
            'title': title,
            'tag': tag,
            'note_path': os.path.join('static', 'uploads', username, pdf_filename),
            'note_img_path': os.path.join('static', 'uploads', username, img_filename) if img_filename else '/static/images/default-note.jpg',
            'about_text': description,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'author': username,
            'visibility': visibility
        }
        
        # Ensure all fieldnames exist in the new note
        for field in fieldnames:
            if field not in new_note:
                new_note[field] = ''  # Add empty value for any missing fields
        
        # Write to CSV
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists or os.path.getsize(csv_path) == 0:
                writer.writeheader()
            writer.writerow(new_note)
        
        flash("Note uploaded successfully!", "success")
        return redirect("/notes")
        
    except Exception as e:
        flash(f"Error uploading note: {str(e)}", "error")
        return redirect("/notes")
    
@app.route('/toggle_visibility/<int:note_id>', methods=['POST'])
def toggle_visibility(note_id):
    if "user" not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    username = session["user"]
    csv_path = os.path.join('data', 'notes_data.csv')
    temp_path = os.path.join('data', 'temp_notes.csv')
    
    try:
        notes = []
        updated = False
        
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if int(row['note_id']) == note_id and row['author'] == username:
                    row['visibility'] = 'public' if row.get('visibility', 'private') == 'private' else 'private'
                    updated = True
                notes.append(row)
        
        if not updated:
            return jsonify({'success': False, 'message': 'Note not found or not authorized'}), 404
        
        # Write back all notes with updated visibility
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(notes)
        
        return jsonify({
            'success': True,
            'new_visibility': row['visibility'],
            'new_icon': 'lock' if row['visibility'] == 'private' else 'globe',
            'new_text': 'Make Public' if row['visibility'] == 'private' else 'Make Private'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    
@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    if "user" not in session:
        flash("You must be logged in to delete notes.", "error")
        return redirect("/login")
    
    username = session["user"]
    csv_path = os.path.join('data', 'notes_data.csv')
    temp_path = os.path.join('data', 'temp_notes.csv')
    
    try:
        # Read all notes and filter out the one to delete
        notes = []
        note_to_delete = None
        
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['note_id']) == note_id and row['author'] == username:
                    note_to_delete = row
                else:
                    notes.append(row)
        
        if not note_to_delete:
            flash("Note not found or you don't have permission to delete it", "error")
            return redirect("/notes")
        
        # Write back all notes except the deleted one
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['note_id', 'title', 'tag', 'note_path', 'note_img_path', 'about_text', 'upload_date', 'author']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(notes)
        
        # Delete associated files
        try:
            if os.path.exists(note_to_delete['note_path']):
                os.remove(note_to_delete['note_path'])
            if 'note_img_path' in note_to_delete and note_to_delete['note_img_path'] != '/static/images/default-note.jpg':
                if os.path.exists(note_to_delete['note_img_path']):
                    os.remove(note_to_delete['note_img_path'])
        except Exception as e:
            flash(f"Note deleted but error removing files: {str(e)}", "warning")
        
        flash("Note deleted successfully!", "success")
        return redirect("/notes")
    
    except Exception as e:
        flash(f"Error deleting note: {str(e)}", "error")
        return redirect("/notes")

@app.route('/view_note/<int:note_id>')
def view_note(note_id):
    if "user" not in session:
        flash("Please log in to view notes.", "error")
        return redirect("/login")
    
    csv_path = os.path.join('data', 'notes_data.csv')
    note = None
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['note_id']) == note_id:
                    if row['visibility'] == 'public' or row['author'] == session["user"]:
                        note = row
                    break
    except Exception as e:
        flash(f"Error loading note: {str(e)}", "error")
    
    if not note:
        flash("Note not found or not authorized", "error")
        return redirect("/notes")
    
    return render_template("view_note.html", note=note)
@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if "user" not in session:
        flash("You must be logged in to edit notes.", "error")
        return redirect("/login")

    username = session["user"]
    csv_path = os.path.join('data', 'notes_data.csv')

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_desc = request.form.get('description')
        new_tag = request.form.get('tag')

        notes = []
        updated = False

        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if int(row['note_id']) == note_id and row['author'] == username:
                    row['title'] = new_title
                    row['about_text'] = new_desc
                    row['tag'] = new_tag
                    updated = True
                notes.append(row)

        if updated:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(notes)
            flash("Note updated successfully!", "success")
        else:
            flash("Note not found or not authorized", "error")

        return redirect("/notes")

    # For GET request
    note = None
    with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['note_id']) == note_id and row['author'] == username:
                note = row
                break

    if not note:
        flash("Note not found or not authorized", "error")
        return redirect("/notes")

    return render_template("edit_note.html", note=note)


@app.route('/search_notes')
def search_notes():
    query = request.args.get('q', '').lower()
    username = session.get("user", None)

    results = []
    csv_path = os.path.join('data', 'notes_data.csv')

    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['visibility'] == 'public' or row['author'] == username) and \
                   (query in row['title'].lower() or query in row['about_text'].lower()):
                    results.append(row)
    except:
        return jsonify([])

    return jsonify(results)

@app.route('/api/notes')
def api_notes():
    csv_path = os.path.join('data', 'notes_data.csv')
    notes = []
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            notes = list(reader)
    except:
        pass
    return jsonify(notes)


@app.route('/profile')
def profile():
    if "user" not in session:
        flash("You must be logged in to view your profile.", "error")
        return redirect("/login")
    
    username = session["user"]
    user = get_user(username)
    
    if not user:
        flash("User not found.", "error")
        return redirect("/dashboard")
    
    # Calculate user statistics
    stats = {
        'notes_count': 0,
        'verified': user.get('is_verified', 'False') == 'True',
        'member_since': '',
        'last_login': ''
    }
    # In your route
    if stats.get('member_since'):
        try:
            join_date = datetime.strptime(stats['member_since'], '%Y-%m-%d')
            stats['days_active'] = (datetime.now() - join_date).days
        except:
            stats['days_active'] = 'N/A'
    else:
        stats['days_active'] = 'N/A'

        # Count user's notes
    csv_path = os.path.join('data', 'notes_data.csv')
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            stats['notes_count'] = sum(1 for row in reader if row['author'] in (username, '{{user}}'))
    
    # Get user data from user_data.csv if exists
    user_data_path = 'user_data.csv'
    if os.path.exists(user_data_path):
        with open(user_data_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username:
                    stats['member_since'] = row.get('join_date', 'Unknown')
                    stats['last_login'] = row.get('last_login', 'Unknown')
                    break
    return render_template("profile.html",
                         user=username,
                         email=user['email'],
                         stats=stats,
                         verified=stats['verified'],
                         datetime=datetime,)  # Pass datetime to template
@app.route('/verify/resend')
def resend_verification():
    if "user" not in session:
        flash("You must be logged in to resend verification.", "error")
        return redirect("/login")
    
    user = get_user(session["user"])
    if not user:
        flash("User not found.", "error")
        return redirect("/profile")
    
    if user.get('is_verified', 'False') == 'True':
        flash("Your account is already verified.", "info")
        return redirect("/profile")
    
    token = secrets.token_urlsafe(32)
    update_user("token", token, user["email"])
    
    send_email(user["email"], "Verify Your Account",
             f"Click here to verify: {request.url_root}verify/{token}")
    
    flash("Verification email resent. Please check your inbox.", "success")
    return redirect("/profile")    

@app.route('/404')
def not_found():
    return render_template("404.html"), 404


# route to code page

@app.route('/codes')
def codes():
    if "user" not in session:
        flash("You must be logged in to access the page.", "error")
        return redirect("/login")
    
    username = session["user"]
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of codes per page
    codes_data = []
    
    # Path to your CSV file for codes
    csv_path = os.path.join('data', 'codes_data.csv')
    
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # Filter codes for current user and public codes
            user_codes = []
            for row in reader:
                if row.get('visibility', 'private') == 'public' or row['author'] == username:
                    if row['author'] == '{{user}}':
                        row['author'] = username
                    user_codes.append(row)
                    
            # Calculate pagination
            total_codes = len(user_codes)
            total_pages = ceil(total_codes / per_page)
            
            # Validate page number
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages
            
            # Get codes for current page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            codes_data = user_codes[start_idx:end_idx]
            
    except FileNotFoundError:
        flash("Codes database not found", "error")
    except Exception as e:
        flash(f"Error loading codes: {str(e)}", "error")
    
    return render_template("codes.html", 
                         user=username,
                         codes=codes_data,
                         page=page,
                         total_pages=total_pages,
                         total_codes=total_codes)

@app.route('/download_code/<int:code_id>')
def download_code(code_id):
    if "user" not in session:
        flash("You must be logged in to download codes.", "error")
        return redirect("/login")
    
    # Find the code in CSV
    csv_path = os.path.join('data', 'codes_data.csv')
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['code_id']) == code_id and row['author'] in (session["user"], '{{user}}'):
                    code_path = row['code_path']
                    # Ensure the path is safe and within allowed directories
                    safe_path = os.path.normpath(code_path)
                    if not safe_path.startswith('static/'):
                        flash("Invalid file path", "error")
                        return redirect("/codes")
                    
                    directory = os.path.dirname(safe_path)
                    filename = os.path.basename(safe_path)
                    
                    # Check if file exists
                    if not os.path.exists(os.path.join(directory, filename)):
                        flash("File not found on server", "error")
                        return redirect("/codes")
                    
                    return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        flash(f"Error downloading code: {str(e)}", "error")
    
    flash("Code not found", "error")
    return redirect("/codes")

@app.route('/upload_code', methods=['POST'])
def upload_code():
    if "user" not in session:
        flash("You must be logged in to upload codes.", "error")
        return redirect("/login")
    
    username = session["user"]
    
    try:
        # Get form data
        title = request.form.get('codeTitle')
        tag = request.form.get('codeTag')
        description = request.form.get('codeDescription')
        code_file = request.files.get('codeFile')
        code_image = request.files.get('codeImage')
        visibility = request.form.get('codeVisibility', 'private')  # Default to private if not specified
        
        # Validate required fields
        if not all([title, tag, description, code_file]):
            flash("All required fields must be filled", "error")
            return redirect("/codes")
        
        # Validate file type (allow common code file types)
        allowed_extensions = ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.ipynb', '.zip', '.rar']
        file_ext = os.path.splitext(code_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            flash("Only code files are allowed (.py, .js, .java, .cpp, .c, .html, .css, .ipynb, .zip, .rar)", "error")
            return redirect("/codes")
        
        # Generate new code ID
        csv_path = os.path.join('data', 'codes_data.csv')
        code_id = 1
        
        # Get existing fieldnames if file exists
        fieldnames = ['code_id', 'title', 'tag', 'code_path', 'code_img_path', 'about_text', 'upload_date', 'author', 'visibility']
        
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                existing_ids = [int(row['code_id']) for row in reader if row['code_id'].isdigit()]
                if existing_ids:
                    code_id = max(existing_ids) + 1
                
                # Update fieldnames from existing file if it has more fields
                if reader.fieldnames:
                    fieldnames = list(reader.fieldnames)
                    if 'visibility' not in fieldnames:
                        fieldnames.append('visibility')
        
        # Save uploaded files
        upload_dir = os.path.join('static', 'uploads', username, 'codes')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save code file
        code_filename = f"code_{code_id}{file_ext}"
        code_path = os.path.join(upload_dir, code_filename)
        code_file.save(code_path)
        
        # Save image if provided
        img_filename = None
        if code_image and code_image.filename:
            img_ext = os.path.splitext(code_image.filename)[1].lower()
            if img_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                img_filename = f"preview_{code_id}{img_ext}"
                img_path = os.path.join(upload_dir, img_filename)
                code_image.save(img_path)
        
        # Add new code to CSV
        new_code = {
            'code_id': str(code_id),
            'title': title,
            'tag': tag,
            'code_path': os.path.join('static', 'uploads', username, 'codes', code_filename),
            'code_img_path': os.path.join('static', 'uploads', username, 'codes', img_filename) if img_filename else '/static/images/default-code.jpg',
            'about_text': description,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'author': username,
            'visibility': visibility
        }
        
        # Ensure all fieldnames exist in the new code
        for field in fieldnames:
            if field not in new_code:
                new_code[field] = ''  # Add empty value for any missing fields
        
        # Write to CSV
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists or os.path.getsize(csv_path) == 0:
                writer.writeheader()
            writer.writerow(new_code)
        
        flash("Code uploaded successfully!", "success")
        return redirect("/codes")
        
    except Exception as e:
        flash(f"Error uploading code: {str(e)}", "error")
        return redirect("/codes")
    
@app.route('/toggle_code_visibility/<int:code_id>', methods=['POST'])
def toggle_code_visibility(code_id):
    if "user" not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    username = session["user"]
    csv_path = os.path.join('data', 'codes_data.csv')
    
    try:
        codes = []
        updated = False
        
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if int(row['code_id']) == code_id and row['author'] == username:
                    row['visibility'] = 'public' if row.get('visibility', 'private') == 'private' else 'private'
                    updated = True
                codes.append(row)
        
        if not updated:
            return jsonify({'success': False, 'message': 'Code not found or not authorized'}), 404
        
        # Write back all codes with updated visibility
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(codes)
        
        return jsonify({
            'success': True,
            'new_visibility': row['visibility'],
            'new_icon': 'lock' if row['visibility'] == 'private' else 'globe',
            'new_text': 'Make Public' if row['visibility'] == 'private' else 'Make Private'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/delete_code/<int:code_id>', methods=['POST'])
def delete_code(code_id):
    if "user" not in session:
        flash("You must be logged in to delete codes.", "error")
        return redirect("/login")
    
    username = session["user"]
    csv_path = os.path.join('data', 'codes_data.csv')
    
    try:
        # Read all codes and filter out the one to delete
        codes = []
        code_to_delete = None
        
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row['code_id']) == code_id and row['author'] == username:
                    code_to_delete = row
                else:
                    codes.append(row)
        
        if not code_to_delete:
            flash("Code not found or you don't have permission to delete it", "error")
            return redirect("/codes")
        
        # Write back all codes except the deleted one
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['code_id', 'title', 'tag', 'code_path', 'code_img_path', 'about_text', 'upload_date', 'author', 'visibility']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(codes)
        
        # Delete associated files
        try:
            if os.path.exists(code_to_delete['code_path']):
                os.remove(code_to_delete['code_path'])
            if 'code_img_path' in code_to_delete and code_to_delete['code_img_path'] != '/static/images/default-code.jpg':
                if os.path.exists(code_to_delete['code_img_path']):
                    os.remove(code_to_delete['code_img_path'])
        except Exception as e:
            flash(f"Code deleted but error removing files: {str(e)}", "warning")
        
        flash("Code deleted successfully!", "success")
        return redirect("/codes")
    
    except Exception as e:
        flash(f"Error deleting code: {str(e)}", "error")
        return redirect("/codes")

# projects route
@app.route('/projects')
def projects():
    if "user" not in session:
        flash("You must be logged in to access the page.", "error")
        return redirect("/login")
    
    username = session["user"]
    return render_template("models.html", user=username)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404  
    

if __name__ == "__main__":
    try:
        with open("secrets.json") as f:
            config = json.load(f)
    except Exception as e:
        print("Warning: No email config found. Using default credentials.")
        config = {
            "EMAIL": "llaka2937@gmail.com",
            "PASSWORD": "hqim uqwh qlkb jpde"
        }

    app.run()

