from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__, static_folder='static')
CORS(app)

app.secret_key = '4fa5155d43b449e48481436f8eb1ee4dre'

# Database connection helper
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@123",
        database="social"
    )

@app.route("/")
def index():
    flash('You were successfully logged in')
    return render_template("index.html")

@app.route('/home')
def dashboard():
    if session.get('loggedin'):
        loggedinuser = session['username']
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE id = %s", [session['id']])
        users = cur.fetchone()

        cur.execute("SELECT * FROM posts WHERE user_id = %s", [session['id']])
        posts = cur.fetchall()

        cur.execute("SELECT * FROM users where id != %s", [session['id']])
        user_account = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("home.html", users=users, posts=posts, loggedinuser=loggedinuser, user_account=user_account)
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('register'))

    return render_template("login.html")

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return render_template('forgotpassword.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cur.fetchone()

        if user:
            return "User already exists"
        else:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            conn.commit()
            cur.close()
            conn.close()
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('profile', username=username))

    return render_template("register.html")

@app.route('/profile/<username>')
def profile(username):
    if session.get('loggedin'):
        return render_template("profile.html", username=username)
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        content = request.form.get('content')
        location = request.form.get('location')
        image = request.files['image']
        tags = request.form.get('tags')

        if image:
            os.makedirs("static/images", exist_ok=True)
            image.save(f"static/images/{image.filename}")
            image_path = f"static/images/{image.filename}"
        else:
            image_path = None

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (content, image, location, tags, user_id) VALUES (%s, %s, %s, %s, %s)", (content, image_path, location, tags, session['id']))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template("post.html")

@app.route('/like', methods=['POST'])
def like():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT likes FROM posts WHERE user_id = %s", [session['id']])
    likes = cur.fetchone()

    if not likes:
        return "No post found for this user", 404

    current_likes = likes[0] or 0
    current_likes += 1

    cur.execute("UPDATE posts SET likes = %s WHERE user_id = %s", (current_likes, session['id']))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'updated_likes': current_likes})

@app.route('/comments', methods=['POST'])
def comment():
    comments = request.form.get('comment')
    post_id = request.form.get('post_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (comment, post_id, user_id) VALUES (%s, %s, %s)", (comments, post_id, session['id']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/home')

@app.route('/share')
def share():
    return "Shared the post!"

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE id = %s", [session['id']])
    users = cur.fetchall()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        image = request.files['profile_image']

        if image:
            os.makedirs("static/images", exist_ok=True)
            image.save(f"static/images/{image.filename}")
            image_path = f"static/images/{image.filename}"
        else:
            image_path = None

        cur.execute("""
            UPDATE users 
            SET username = %s, email = %s, password = %s, profile_image = %s
            WHERE id = %s
        """, (username, email, password, image_path, session['id']))
        conn.commit()

        session['username'] = username
        return redirect(url_for('settings'))

    cur.close()
    conn.close()

    return render_template("settings.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)
