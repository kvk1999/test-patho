from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'path123'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def send_reset_email(email):
    sender_email = "your_email@example.com"  # Your email address
    receiver_email = email  # Recipient's email address
    password = "your_email_password"  # Your email account password

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"""\
    Hi,
    Click on the link below to reset your password:
    http://yourwebsite.com/reset_password?email={email}"""

    part = MIMEText(text, "plain")
    message.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.example.com', 465)  # SMTP server and port for SSL
        server.login(sender_email, password)  # Log in to the server
        server.sendmail(sender_email, receiver_email, message.as_string())  # Send email
        server.quit()  # Close the connection
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
            conn.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists')
            return redirect(url_for('signup'))
        finally:
            conn.close()
    return render_template("signup.html")

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user:
            send_reset_email(email)
            flash('Password reset instructions have been sent to your email.')
        else:
            flash('Email not found')
    return render_template("forgot.html")

@app.route('/chat')
def chat():
    return render_template("chat.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/buy')
def buy():
    return render_template("buy.html")

@app.route('/payment')
def payment():
    return render_template("Payment.html")

@app.route('/pathorepo')
def pathorepo():
    return render_template("pathorepo.html")

@app.route('/bookanappointment')
def bookanappointment():
    return render_template("bookanappointment.html")

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
