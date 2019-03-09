from flask import Flask, render_template, request, session
import os
import uuid
import hashlib
import pymysql.cursors

app = Flask(__name__)
IMAGES_DIR = os.path.join(os.getcwd(), "images")

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='finsta',
                             charset='utf8mb4',
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['GET'])
def upload():
    return render_template("upload.html")

@app.route("/login", methods=['GET'])
def login():
    return render_template("login.html")

@app.route("/register", methods=['GET'])
def register():
    return render_template("register.html")

@app.route("/loginAuth", methods=["POST"])
def loginAuth():
    return "logging in"

@app.route("/registerAuth", methods=["POST"])
def registerAuth():
    if request.form:
        requestData = request.form
        username = requestData['username']
        plaintextPasword = requestData['password']
        firstName = requestData['fname']
        lastName = requestData['lname']
        with connection.cursor() as cursor:
            sql = "INSERT INTO person (username, password, fname, lname) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, plaintextPasword, firstName, lastName))
        return "Done registering"
    return "Failed to register"

@app.route("/uploadImage", methods=["POST"])
def upload_image():
    if request.files:
        image_file = request.files.get('imageToUpload', '')
        image_name = image_file.filename
        image_extension = os.path.splitext(image_name)[1]
        image_uuid = str(uuid.uuid4())
        new_image_filename = image_uuid + image_extension
        image_file.save(os.path.join(IMAGES_DIR, new_image_filename))
        return "Uploaded image"
    else:
        return "Done"

if __name__ == "__main__":
    if not os.path.isdir("images"):
        os.mkdir(IMAGES_DIR)
    app.run()
