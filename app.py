from flask import Flask, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import hashlib
import pymysql.cursors
from functools import wraps
import time

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
import tools
import insert_photo
import tag_logic
import add_new_tag
import comments


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
    return render_template("upload.html", user_groups=tools._get_current_user_groups())

@app.route("/follow", methods=["GET"])
@login_required
def follow_page():
    followReq = getFollowRequest()
    return render_template("follow.html", followReq =followReq, following = getFollowing())

@app.route("/friends", methods=["GET"])
@login_required
def friends():
    groups = getFriendGroups()
    return render_template("friends.html", friendGroup = groups)

#images which get passed to the image gallery
#this send the image with all of it's data too
#A photo is visible to a user U if either
#   U has been accepted as a follower by teh owner of the photo or
#   The photo is shared with a CloseFriendGroup to which U belongs
@app.route("/images", methods=["GET"])
@login_required
def images():
    posts= []
    username = session['username']
    query = 'SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM  Photo, Belong, Share Where belong.username = %s and belong.groupOwner = share.groupOwner AND Belong.groupName = share.groupName AND photo.photoID = share.photoID UNION (SELECT Photo.photoID, timestamp, filePath, photoOwner, caption FROM Photo, Follow  WHERE (photoOwner = %s ) or (followerUsername = %s AND photoOwner = followeeUsername AND acceptedfollow = TRUE)) ORDER BY Timestamp DESC'
    query2 = "SELECT * FROM Person NATURAL JOIN Tag NATURAL JOIN Photo WHERE Photo.photoID = %s AND acceptedTag = True"
    with connection.cursor() as cursor:
        cursor.execute(query, (username, username, username))
    data = cursor.fetchall()
    for post in data:
          with connection.cursor() as cursor:
            cursor.execute(query2, (post["photoID"]))
          tags = cursor.fetchall() 
          posts.append(tags) 
    print(posts)
    return render_template("images.html", images=data, posts = posts)

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

@app.route("/create_group", methods = ["POST"])
@login_required
def createGroup():
    request_data = request.form
    groupName = request_data['groupName']
    query = "SELECT * FROM CloseFriendGroup WHERE groupName = %s AND groupOwner = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (groupName, session['username']))
    data = cursor.fetchall()
    if len(data)>0:
        error = "Friend group with name : %s already exist" % (groupName)
        return render_template('friends.html', error=error, friendGroup = getFriendGroups())
    else:
        query = "INSERT INTO CloseFriendGroup VALUES (%s, %s); "
        with connection.cursor() as cursor:
            cursor.execute(query, (groupName, session["username"]))
        query = "INSERT INTO Belong VALUES (%s, %s, %s); "
        with connection.cursor() as cursor:
            cursor.execute(query, (groupName, session["username"], session["username"]))
    return redirect("/friends")

@app.route("/removeFriend", methods = ["POST"])
@login_required
def removeFriend():
    request_data = request.form
    username = request_data['username']
    group = request_data['groupName']
    query = "SELECT * FROM Belong WHERE username = %s AND groupName = %s AND username != %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (username, group, session["username"]))
    data = cursor.fetchall()
    if len(data) == 0:
        error = "The username: "+ username+" is not in the friend group or is the group Owner"
        return render_template('friends.html', error=error, friendGroup = getFriendGroups())
    else:
        query = "DELETE FROM Belong WHERE username = %s and groupName = %s "
        with connection.cursor() as cursor:
            cursor.execute(query, (username, group))

    return redirect("/friends")


@app.route("/friendGroup", methods = ["POST"])
@login_required
def friendGroup():
    request_data = request.form
    username = request_data['username']
    group = request_data['groupName']
    query = "SELECT * FROM Person WHERE username = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, username)
    data = cursor.fetchall()
    if len(data)>0:
        query = "SELECT * FROM Belong WHERE (username = %s or username = %s) AND groupName = %s AND groupOwner = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (username, session["username"], group, session["username"]))
        data = cursor.fetchall()
        if len(data)>0:
            error = "User: {} already in group: {}".format(username, group)
            return render_template('friends.html', error=error, friendGroup = getFriendGroups())
        else:
            query = "INSERT INTO Belong Values(%s, %s, %s)"
            with connection.cursor() as cursor:
                cursor.execute(query, (group, session["username"], username))
    else:
        error = username + " is not a valid username."
        return render_template('friends.html', error=error, friendGroup = getFriendGroups())
    return redirect("/friends")


def getFriendGroups():
    query = "SELECT groupName FROM Belong WHERE username = %s AND groupOwner = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (session["username"], session["username"]))
    data = cursor.fetchall()
    return data

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
            return render_template('follow.html', error=error, followReq = getFollowRequest(), following = getFollowing())
        else:
            query = "INSERT INTO Follow VALUES (%s, %s, False); "
            with connection.cursor() as cursor:
                cursor.execute(query, (session["username"], username))
    else:
        error = "%s is not a valid username." % (username)
        return render_template('follow.html', error=error, followReq = getFollowRequest(), following = getFollowing())
    return redirect("/follow")


def getFollowRequest():
    query = "SELECT followerUsername FROM Follow WHERE followeeUsername = %s and acceptedfollow = False"
    with connection.cursor() as cursor:
        cursor.execute(query, session["username"])
    data = cursor.fetchall()
    return data

def getFollowing():
    query = "SELECT followeeUsername FROM Follow WHERE followerUsername = %s and acceptedfollow = True"
    with connection.cursor() as cursor:
        cursor.execute(query, session["username"])
    data = cursor.fetchall()
    return data

@app.route("/unfollow", methods = ["POST"])
@login_required
def unfollow():
    request_data = request.form
    print(request_data)
    username = request_data["username"]
    query = "DELETE FROM follow WHERE followerUsername = %s AND followeeUsername = %s AND acceptedfollow = True"
    print(query)
    with connection.cursor() as cursor:
        print(session['username'], username)
        cursor.execute(query, (session["username"], username))
    query = "DELETE FROM Tag WHERE username = %s AND photoID in (select * from (SELECT photoID from tag NATURAL JOIN Photo where photoOwner = %s) as t)"
    with connection.cursor() as cursor:
            cursor.execute(query, (session["username"], username))
    return redirect("/follow")





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
#add tag to the image
@app.route("/add_tag", methods=["POST", "GET"])
@login_required
def add_tag():
    return add_new_tag.new_tag()

@app.route("/view_tags", methods=["GET"])
@login_required
def view_tags():
    user_tag_requests = tag_logic.get_user_tag_requests()
    return render_template("tags.html", user_tags=user_tag_requests)

@app.route("/tag_action", methods=["POST"])
def tag_action():
    tag_logic.submit_tag_action()
    return redirect("/view_tags")

@app.route("/comment", methods=["POST"])
@login_required
def post_comment():
    comments.submit_comment()
    return redirect("/images")

if __name__ == "__main__":
    app.run(debug = True)
    if not os.path.isdir("images"):
        os.mkdir(IMAGES_DIR)
    app.run()
