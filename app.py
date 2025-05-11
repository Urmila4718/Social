from email.mime import image
from flask import Flask, flash, jsonify, make_response, redirect,render_template, request, session, url_for
from sqlalchemy import true
import bcrypt 
from flask_mysqldb import MySQL
from flask_cors import CORS


app = Flask(__name__,static_folder='static')
CORS(app) 


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= 'Root@123'
app.config['MYSQL_DB']= 'social'
app.secret_key = '4fa5155d43b449e48481436f8eb1ee4dre'

mysql = MySQL(app)


#---------------------------------------------------------------Index Page--------------------------------------------------
@app.route("/")
def index():
    flash('You were successfully logged in')
    return render_template("index.html")

#---------------------------------------------------------------Home Page--------------------------------------------------
@app.route('/home')
def dashboard():
    if session.get('loggedin'):
        loggedinuser = session['username']

        if loggedinuser:
            cur = mysql.connection.cursor()

            # Get the user once
            cur.execute("SELECT * FROM users WHERE id = %s", [session['id']])
            users = cur.fetchone()
            print(users)

            # Get all posts by that user
            cur.execute("SELECT * FROM posts WHERE user_id = %s", [session['id']])
            posts = cur.fetchall()
            print(posts)


            
            cur.execute("SELECT * FROM users where id != %s", [session['id']])
            user_account = cur.fetchall()
            
        return render_template("home.html", users=users, posts= posts, loggedinuser=loggedinuser, user_account=user_account)
    else:
        return redirect('/login')


#---------------------------------------------------------------Login Page--------------------------------------------------
@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username,password))
        user = cur.fetchone()
        if user != None:
            if user[2] == password:
                print("fdjfhduhg")
                session['loggedin'] = True
                session['id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard')) 
            else:
                return "Password is incorrect"
        else:
            return redirect(url_for('register')) 

    return render_template("login.html")

@app.route('/forgotpassword', methods =['GET','POST'])
def forgotpassword():
    
    return render_template('forgotpassword.html')   
#---------------------------------------------------------------Register Page--------------------------------------------------
@app.route('/register', methods =['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s ", [username])
        user = cur.fetchone()
        if user:
             return "User already exists"
        else:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            mysql.connection.commit()
            cur.close()
            session['loggedin'] = True
            session['username'] = username
      
            return redirect(url_for('profile', username=username))

    return render_template("register.html")


#---------------------------------------------------------------Profile Page--------------------------------------------------
@app.route('/profile/<username>')
def profile(username):
    if session.get('loggedin'):
        return render_template("profile.html",username=username)
    else:
        return redirect('/login')

#---------------------------------------------------------------Logout Page--------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')

#---------------------------------------------------------------About Pages--------------------------------------------------
@app.route('/about')
def about():
    return render_template("about.html")

#---------------------------------------------------------------Contact Pages--------------------------------------------------
@app.route('/contact')
def contact():
    return render_template("contact.html")

#---------------------------------------------------------------Post Pages--------------------------------------------------
@app.route('/post',methods =['GET','POST']) 
def post():
    if request.method == 'POST':
        content = request.form.get('content')

        location = request.form.get('location')

        image = request.files['image']
    
        tags = request.form.get('tags')
      
        if image:   
            image.save(f"static/images/{image.filename}")
            image_path = f"static/images/{image.filename}"
        else:
            image_path = None   
        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO posts (content, image,location, tags,user_id) VALUES (%s, %s,%s, %s,%s)", (content, image_path,location, tags, session['id']))
        mysql.connection.commit()
        return redirect(url_for('dashboard')) 

    return render_template("post.html")

#----------------------------------------------------------------Like Pages--------------------------------------------------   
@app.route('/like', methods=['POST'])
def like():
    cur = mysql.connection.cursor()
    cur.execute("SELECT likes FROM posts WHERE user_id = %s", [session['id']])
    likes = cur.fetchall()

    if not likes:
        return "No post found for this user", 404  

    current_likes = likes[0][0]  

    if current_likes is None:
        current_likes = 0
    current_likes += 1

    cur.execute("UPDATE posts SET likes = %s WHERE user_id = %s", (current_likes, session['id']))
    mysql.connection.commit()

    return jsonify({'updated_likes': current_likes})

#---------------------------------------------------------------Comment Pages--------------------------------------------------
@app.route('/comments',methods=['GET','POST'])
def comment():
    comments = request.form.get('comment')
    post_id = request.form.get('post_id')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO comments (comment, post_id, user_id) VALUES (%s, %s,%s)", (comments, post_id,session['id']))
    mysql.connection.commit()
    return redirect('/home')

#---------------------------------------------------------------Share Pages--------------------------------------------------
@app.route('/share')
def share():
    return  "Shared the post!"

#---------------------------------------------------------------Settings Pages--------------------------------------------------
@app.route('/settings',methods=['GET', 'POST'])
def settings():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users where id = %s", [session['id']])
    users = cur.fetchall()
    
    if request.method == 'POST':
        loggedinuser = session['username']

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        image =   request.files['profile_image'] 
        if image:   
            image.save(f"static/images/{image.filename}")
            image_path = f"static/images/{image.filename}"
        else:
            image_path = None   

        
        cur.execute("""
        UPDATE users 
        SET username = %s, email = %s, password = %s , profile_image = %s
        WHERE username = %s
        """, (username, email, password, image_path,loggedinuser))
        mysql.connection.commit()

        session['username'] = username
        loggedinuser = session['username']
        return redirect(url_for('settings')) 

    return render_template("settings.html",users=users) 
    

























if __name__ == "__main__":
    app.run(debug=True)
