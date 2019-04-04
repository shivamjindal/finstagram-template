from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
import pymysql.cursors
from functools import wraps
import time
import insert_photo

app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.getcwd(), "images")

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root",
                             db="finsta",
                             charset="utf8mb4",
                             port=8889,
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=True)

def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not "username" in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return dec

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html", username=session["username"])

@app.route("/upload", methods=["GET"])
@login_required
def upload():
    return render_template("upload.html")

@app.route("/follow", methods=["GET"])
@login_required
def follow_page():
    followReq = getFollowRequest()
    return render_template("follow.html", followReq =followReq)

#images which get passed to the image gallery 
#this send the image with all of it's data too
#A photo is visible to a user U if either 
#   U has been accepted as a follower by teh owner of the photo or
#   The photo is shared with a CloseFriendGroup to which U belongs
@app.route("/images", methods=["GET"])
@login_required
def images():
    #do everything in one query 
    query = "SELECT DISTINCT Photo.photoID, photoOwner, timestamp, filePath, caption, allFollowers FROM Photo INNER JOIN Follow WHERE photoOwner = followerUsername AND acceptedfollow = TRUE ORDER BY Timestamp DESC" 
    with connection.cursor() as cursor:
        cursor.execute(query)
    data = cursor.fetchall()
    return render_template("images.html", images=data)

@app.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    image_location = os.path.join(IMAGES_DIR, image_name)
    if os.path.isfile(image_location):
        return send_file(image_location, mimetype="image/jpg")



@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/loginAuth", methods=["POST"])
def loginAuth():
    if request.form:
        requestData = request.form
        username = requestData["username"]
        plaintextPasword = requestData["password"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()

        with connection.cursor() as cursor:
            query = "SELECT * FROM person WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashedPassword))
        data = cursor.fetchone()
        if data:
            session["username"] = username
            return redirect(url_for("home"))

        error = "Incorrect username or password."
        return render_template("login.html", error=error)

    error = "An unknown error has occurred. Please try again."
    return render_template("login.html", error=error)

@app.route("/registerAuth", methods=["POST"])
def registerAuth():
    if request.form:
        requestData = request.form
        username = requestData["username"]
        plaintextPasword = requestData["password"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        firstName = requestData["fname"]
        lastName = requestData["lname"]
        
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO person (username, password, fname, lname) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (username, hashedPassword, firstName, lastName))
        except pymysql.err.IntegrityError:
            error = "%s is already taken." % (username)
            return render_template('register.html', error=error)    

        return redirect(url_for("login"))

    error = "An error has occurred. Please try again."
    return render_template("register.html", error=error)


@app.route("/follow_req", methods = ["POST"])
@login_required
def follow():
    request_data = request.form
    username = request_data['username']
    query = "SELECT * FROM Person WHERE username = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, username)
    data = cursor.fetchall()
    if len(data)>0:
        query = "SELECT * FROM Follow WHERE followeeUsername = %s AND followerUsername = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (username, session["username"]))
        data = cursor.fetchall()
        if len(data)>0:
            error = "Request already sent to %s" % (username)
            return render_template('follow.html', error=error, followReq = getFollowRequest())
        else:
            query = "INSERT INTO Follow VALUES (%s, %s, False); "
            with connection.cursor() as cursor:
                cursor.execute(query, (session["username"], username))
    else:
        error = "%s is not a valid username." % (username)
        return render_template('follow.html', error=error, followReq = getFollowRequest())
    return redirect("/follow")



def getFollowRequest():
    query = "SELECT followerUsername FROM Follow WHERE followeeUsername = %s and acceptedfollow = False"
    with connection.cursor() as cursor:
        cursor.execute(query, session["username"])
    data = cursor.fetchall()
    return data

@app.route("/followAction", methods=["POST"])
def followAction():
    request_data = request.form
    response = request_data["response"]
    username = request_data["username"]
    if response == "accept":
        query = "UPDATE follow SET acceptedfollow = True WHERE followerUsername = %s AND followeeUsername = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (username, session["username"]))
    else:
        query = "DELETE FROM follow WHERE followeeUsername = %s and acceptedfollow = False"
        with connection.cursor() as cursor:
            cursor.execute(query, session["username"])
    return redirect("/follow")


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username")
    return redirect("/")

@app.route("/uploadImage", methods=["POST"])
@login_required
def upload_image():
    return insert_photo.upload_image()

if __name__ == "__main__":
    app.run(debug = True)
    if not os.path.isdir("images"):
        os.mkdir(IMAGES_DIR)
    app.run()
